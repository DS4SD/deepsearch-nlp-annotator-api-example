import asyncio
from datetime import datetime, timedelta, timezone
import json
import logging
from nlp_annotator_api.server.middleware.redis_cache import RedisCache
from typing import Any, Optional
import aiohttp.web
from attr import dataclass
import connexion
from connexion.exceptions import ProblemException
from statsd import StatsClient

from nlp_annotator_api.annotators.SimpleTextGeographyAnnotator import SimpleTextGeographyAnnotator
from nlp_annotator_api.annotators.TextTableGeographyAnnotator import TextTableGeographyAnnotator
from nlp_annotator_api.annotators.SimpleTextClassifier import SimpleTextClassifier
from nlp_annotator_api.annotators.ScispacyBiomedAnnotator import ScispacyBiomedAnnotator
from nlp_annotator_api.annotators.WatsonHealthAnnotator import WatsonHealthAnnotator


_log = logging.getLogger(__name__)

# If you have several annotators, import them all here in the same way,
# and put them in the following dictionary:
annotators = {
    'SimpleTextGeographyAnnotator': SimpleTextGeographyAnnotator(),
    'TextTableGeographyAnnotator': TextTableGeographyAnnotator(),
    'SimpleTextClassifier': SimpleTextClassifier(),
    'ScispacyBiomedAnnotator': ScispacyBiomedAnnotator(),
    'WatsonHealthAnnotator': WatsonHealthAnnotator()
}


# Return the name of all annotators callable in this API
def get_annotator_definitions():
    return list(annotators.keys())


@dataclass
class _TimingParameters:
    deadline: Optional[datetime] = None
    transaction_id: Optional[str] = None

    attempt_number: Optional[int] = None
    max_attempts: Optional[int] = None


def _get_timing_parameters(request: aiohttp.web.Request):
    parameters = _TimingParameters()

    x_cps_deadline: Optional[str] = request.headers.get("X-CPS-Deadline")
    x_cps_transaction_id: Optional[str] = request.headers.get("X-CPS-Transaction-Id")
    x_cps_attempt_number: Optional[str] = request.headers.get("X-CPS-Attempt-Number")
    x_cps_max_attempts: Optional[str] = request.headers.get("X-CPS-Max-Attempts")

    if x_cps_deadline:
        parameters.deadline = datetime.fromisoformat(x_cps_deadline)

    if x_cps_transaction_id:
        parameters.transaction_id = x_cps_transaction_id

    if x_cps_attempt_number:
        parameters.attempt_number = int(x_cps_attempt_number)

    if x_cps_max_attempts:
        parameters.max_attempts = int(x_cps_max_attempts)

    return parameters


async def _get_cached_response(params: _TimingParameters, request: aiohttp.web.Request):
    cache: Optional[RedisCache] = request.config_dict.get("redis_cache")

    if not params.transaction_id or cache is None:
        return

    _log.info("Checking for id=%r in cache", params.transaction_id)

    result_str = await cache.get(params.transaction_id)

    if result_str is not None:
        _log.info("Value for id=%r is cached", params.transaction_id)
        return json.loads(result_str)

    _log.info("Value for id=%r not in cache", params.transaction_id)

    return None


async def _store_response(params: _TimingParameters, value: Any, request: aiohttp.web.Request):
    cache: Optional[RedisCache] = request.config_dict.get("redis_cache")

    if not params.transaction_id or cache is None:
        return
    
    # Check if we should store the cached value at all.
    # No point in checking if we are well in the client's deadline.
    if params.deadline is not None:
        # Allow for some clock skew
        now = datetime.now(tz=timezone.utc) - timedelta(seconds=10)

        if params.deadline < now:
            _log.info("We are within the deadline, not caching")
            return

    _log.info("Storing result id=%r in cache", params.transaction_id)

    await cache.set(params.transaction_id, json.dumps(value))


async def run_nlp_annotator(
    annotator: str,
    body: dict, 
    request: aiohttp.web.Request, 
):
    timing_params = _get_timing_parameters(request)

    cached_response = await _get_cached_response(timing_params, request)

    if cached_response is not None:
        return cached_response

    _log.info("Annotating... (id=%r)", timing_params.transaction_id)

    client: StatsClient = request.config_dict['statsd_client']

    with client.pipeline() as pip:
        operation = next(iter(body.keys()))

        if not (annotator in annotators):
            pip.incr(f"run_nlp_annotator.bad_annotator.{operation}.{annotator}.count")
            return connexion.problem(404, 'Not Found', f"Annotator {annotator!r} not found.")

        pip.incr(f"run_nlp_annotator.{operation}.{annotator}.count")

        with pip.timer(f"run_nlp_annotator.{operation}.{annotator}.time"):
            results = _run_annotator(annotators[annotator], body)

        # aiohttp may cancel the coroutine here if the client disconnects.
        # So, shield it from cancellation.
        await asyncio.shield(_store_response(timing_params, results, request))

        return results


def _run_annotator(annot, body):
    if 'find_entities' in body:
        find_entities_part = body['find_entities']
        #print("---- 'Find_entities' part of the request: -----") ## For debugging
        #print(find_entities_part)
        #
        ## Here an example of 'find_entities_part' for text:
        # {
        #     'texts': [
        #         'some text', 
        #         'more text'
        #     ], 
        #     'object_type': 'text', 
        #     'entity_names': ['materials']
        # }
        ## And for tables:
        # {
        #     'tables': [
        #         [ ## A table :
        #             [ ## A row:
        #                 { ## A cell:
        #                     'bbox': [77.679924, 604.052, 108.66927, 633.82397], 
        #                     'spans': [[0, 0]], 
        #                     'text': 'Fruit', 
        #                     'type': 'col_header'
        #                 }, 
        #                 ...
        #             ]
        #         ]
        #     ], 
        #     'object_type': 'table', 
        #     'entity_names': ['materials']
        # }                    


        items = _validate_and_parse_input(find_entities_part, annot)

        entities = annot.annotate_batched_entities(find_entities_part['object_type'], items, find_entities_part['entity_names'])
        ## Key annotation functionn, depends on object_type (text, table etc.) 

        #print("Result returned from '_run_annotator': ")
        #pprint.pprint({'entities': entities})    
        return {'entities': entities}

    if 'find_relationships' in body:
        find_relationships = body['find_relationships']

        items = _validate_and_parse_input(find_relationships, annot)

        relationships = annot.annotate_batched_relationships(
            items,
            find_relationships['entities'],
            find_relationships['relationship_names'],
        )

        return {'relationships': relationships}

    if 'find_properties' in body:
        find_properties = body['find_properties']

        items = _validate_and_parse_input(find_properties, annot)

        properties = annot.annotate_batched_properties(
            items,
            find_properties['entities'],
            find_properties['property_names'],
        )

        return {'properties': properties}

    if 'features' in body:

        features = body['features']

        result = {
            'entity_names': [],
            'relationship_names': [],
            'property_names': [],
            'supported_object_types': annot.supports,
            'labels': []
        }

        if features.get('entity_names'):
            result['entity_names'] = annot.get_entity_names()

        if features.get('relationship_names'):
            result['relationship_names'] = annot.get_relationship_names()

        if features.get('property_names'):
            result['property_names'] = annot.get_property_names()

        if features.get('labels'):
            result['labels'] = annot.get_labels()

        return result

    return None


def _validate_and_parse_input(body_part, annot):
    ## Input: body_part is the part of the request body indexed by the main command, e.g., body['find_entities']
    ##        ann_cls is one of the Annotator classes in this repository.
    ## Output: "items", i.e., a list of texts, tables, or images, if the request passed validation 
    # Connexion seems to fail to validate the polymorphic inputs, so we need to do it ourselves :(
    object_type = body_part.get('object_type', 'text')

    expected = ('text', 'image', 'table')

    if object_type not in expected:
        raise ProblemException(
            status=400,
            title="Bad Request",
            detail=f"Invalid object type. Expected one of: {expected}"
        )

    if object_type not in annot.supports:
        raise ProblemException(
            status=400,
            title="Bad Request",
            detail=f"Unsupported object type for this annotator. Supports: {annot.supports}",
        )

    if object_type == 'text':
        if not isinstance(body_part.get('texts'), list):
            raise ProblemException(status=400, title="Bad Request", detail="Invalid input: Missing 'texts'")

        return body_part['texts']

    if object_type == 'image':
        if not isinstance(body_part.get('images'), list):
            raise ProblemException(status=400, title="Bad Request", detail="Invalid input: Missing 'images'")

        return body_part['images']

    if object_type == 'table':
        if not isinstance(body_part.get('tables'), list):
            raise ProblemException(status=400, title="Bad Request", detail="Invalid input: Missing 'tables'")

        return body_part['tables']
