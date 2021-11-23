import logging
import re
import time
import requests
from typing import Optional, Any, List, Dict
from json import JSONDecodeError
from requests.auth import HTTPBasicAuth
from nlp_annotator_api.config.config import conf

_camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

logger = logging.getLogger(__name__)

EntityMap = Dict[str, List[dict]]


def _kebab_case(text):
    return _camel_case_pattern.sub('-', text).lower()


class WatsonHealthAnnotator:
    supports = ('text',)

    @staticmethod
    def key():
        return "watson-health-annotator"

    @staticmethod
    def get_labels(parameters=None):
        default_output = {
            'relationships': [],
            'entities': [
                {
                    'key': _kebab_case(k.replace('.', '')),
                    'description': v
                }
                for k, v in conf.watson_health_annotator.concepts.items()
            ],
        }

        return default_output

    def process_entity_names(
        self, entity_names: Optional[List[str]]
    ) -> Optional[List[str]]:
        return key_intersection(self.get_entity_names(), entity_names)

    def get_entity_names(self):
        annotations = self.get_labels()
        return [ent['key'] for ent in annotations['entities']]

    def get_property_names(self) -> Optional[List[str]]:
        return []

    def find_entities(self, text, entity_names, device="cpu") -> EntityMap:
        object_type = "text"
        return next(iter(self.annotate_batched_entities(object_type, [text], entity_names, device=device)), {})

    def annotate_batched_entities(self, object_type: str,  texts: List[str], entity_names, device="cpu") -> List[EntityMap]:
        entity_names = self.process_entity_names(entity_names)

        if is_explicitly_empty(entity_names):
            return [{} for _ in texts]

        # The actual max size is 51200, but let's be safe and do a bit less.
        max_safe_size = 40000
        max_size = 51200

        def chunks_by_size():
            current_chunk_size = 0

            unstructured_texts = []

            for text in texts:

                # Break the current chunk if we reached the chunk limit.
                if current_chunk_size > max_safe_size or len(text) + current_chunk_size > max_size:
                    yield unstructured_texts

                    current_chunk_size = 0
                    unstructured_texts = []

                # Overhead for the JSON payload {"text":""}
                current_chunk_size += 12

                if len(text) > max_safe_size:
                    logger.warning(
                        "Text %r is too long (%r chars). Truncating to a length of %r",
                        text[0:24] + '...', len(text), max_safe_size
                    )

                    text = f"{text[0:max_safe_size]}..."

                current_chunk_size += len(text)
                unstructured_texts.append({'text': text})

            if unstructured_texts:
                yield unstructured_texts

        all_merged = []

        for chunk in chunks_by_size():
            all_merged.extend(self._call_api_on_non_empty_texts(chunk, entity_names))

        return all_merged

    def _call_api_on_non_empty_texts(self, texts_chunk, entity_names) -> list:
        results = []
        indexes_to_annotate = []
        texts_to_annotate = []

        for index, item in enumerate(texts_chunk):
            # The Watson annotator doesn't return results for empty texts.
            # In fact, it will even raise 400s if all we pass to it is empty texts.
            # Therefore, and since we need the indexes to match the input texts,
            # what we do is populate the results list ourselves, padding any 'empty text' index
            # with an empty annotation object. For non-empty texts, we put them into their own list
            # and store the index of the input list. That index is then used to fill the gaps,
            # which are filled with `None` at this stage.
            if not item.get('text'):
                results.append({})
            else:
                indexes_to_annotate.append(index)
                texts_to_annotate.append(item)
                results.append(None)

        annotations = self._call_api(texts_to_annotate, entity_names)

        if len(annotations) != len(texts_to_annotate):
            logger.warning(
                "Got an unexptected amount of results from the API: %r, expected %r. "
                "The list will be filled or truncated to match",
                len(annotations), len(texts_to_annotate)
            )

            if len(annotations) > len(texts_to_annotate):
                # Truncate the excess.
                annotations = annotations[0:len(texts_to_annotate)]

            if len(annotations) < len(texts_to_annotate):
                # Fill with empty annotations.
                annotations = [*annotations, *({} for _ in range(len(texts_to_annotate) - len(annotations)))]

        for index, item_annotations in zip(indexes_to_annotate, annotations):
            results[index] = item_annotations

        return results

    def _call_api(self, texts_chunk, entity_names) -> list:
        if not texts_chunk:
            logger.debug("No input provided, returning nothing.")
            return []

        base_url = conf.watson_health_annotator.api_url
        api_key = conf.watson_health_annotator.api_key
        flow_name = conf.watson_health_annotator.flow_name
        max_attempts = conf.watson_health_annotator.max_attempts
        timeout = conf.watson_health_annotator.timeout_seconds

        attempt = 0
        wait_time_seconds = 5
        data = None

        api_input = {
            'unstructured': texts_chunk,
        }

        while data is None and attempt < max_attempts:
            attempt += 1

            url = f'{base_url}/v1/analyze/{flow_name}'

            logger.debug("Calling %r (attempt %r)", url, attempt)

            response = None

            try:
                response = requests.post(
                    url,
                    params={
                        'version': '2019-04-02',
                        'return_analyzed_text': 'false',
                    },
                    json=api_input,
                    headers={
                        'Accept': 'application/json',
                    },
                    auth=HTTPBasicAuth('apikey', api_key),
                    timeout=timeout,
                )
            except requests.exceptions.RequestException as req_err:
                logger.error("Attempt %r: Request failed entirely!", attempt, exc_info=req_err)

            if response is not None:
                try:
                    response.raise_for_status()
                    data = response.json()
                except JSONDecodeError:
                    logger.error(
                        f"Attempt %r: Annotate endpoint did not produce valid JSON on a 200 response. Text=%r",
                        attempt,
                        response.text,
                    )
                except Exception as http_err:
                    logger.error(
                        "Attempt %r: Annotate endpoint failed with status %r and text %r.",
                        attempt,
                        response.status_code,
                        response.text,
                        exc_info=http_err,
                    )

            time.sleep(wait_time_seconds)

        if data is None:
            logger.error("Annotate endpoint did not produce any valid data after % attempts.", max_attempts)
            return [{} for _ in texts_chunk]

        if entity_names:
            entity_names = list(set(entity_names).intersection(self.get_entity_names()))
        else:
            entity_names = self.get_entity_names()

        texts = (t['text'] for t in texts_chunk)

        if 'unstructured' not in data:
            logger.debug("No 'unstructured' object in the response %r", data)

        unstructured = data.get('unstructured') or [{} for _ in range(len(texts_chunk))]

        return [self._process_data(d, t, entity_names) for d, t in zip(unstructured, texts)]

    def _process_data(self, data, text, entity_names) -> EntityMap:

        if 'data' not in data:
            logger.debug(f"'data' not present in %r for %r", data, text)
            return {}

        if 'concepts' not in data['data']:
            logger.debug(f"'concepts' not present in 'data' %r for %r", data['data'], text)
            return {}

        entities_by_type = {}

        for concept in data['data']['concepts']:
            entity_type = _kebab_case(concept['type'].replace('.', ''))

            if entity_type not in entity_names:
                continue

            entities = entities_by_type.setdefault(entity_type, [])

            entities.append({
                'type': entity_type,
                'original': concept['coveredText'],
                'match': concept['preferredName'],
                'range': [concept['begin'], concept['end']]
            })

            icd10_code_type = _kebab_case("icd10Code".replace('.', ''))
            # If requested, creates additional entities for icd10Code
            if 'icd10Code' in concept and icd10_code_type in entity_names:
                icd10_code_entities = entities_by_type.setdefault(icd10_code_type, [])

                icd10_code_entity = {
                    'type': icd10_code_type,
                    'original': concept['coveredText'],
                    'match': concept['icd10Code'],
                    'range': [concept['begin'], concept['end']]
                }

                if icd10_code_entity not in icd10_code_entities:
                    icd10_code_entities.append(icd10_code_entity)

        return entities_by_type

    def get_relationship_names(self):
        return []

    def find_relationships(self, text: Any, relationship_names, entities: EntityMap = None, device="cpu") -> dict:
        return {}


def is_explicitly_empty(keys: Optional[List[str]]) -> bool:
    """
    Returns if the input keys is explicitly empty, that is, set to an actual empty collection.
    """
    return keys is not None and not keys


def key_intersection(
    a: Optional[List[str]], b: Optional[List[str]]
) -> Optional[List[str]]:
    if a is None and b is None:
        return None

    if a is None:
        return list(b)

    if b is None:
        return list(a)

    return list(set(a) & set(b))
