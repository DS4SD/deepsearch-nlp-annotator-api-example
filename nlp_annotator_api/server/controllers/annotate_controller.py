import aiohttp.web
import connexion
from connexion.exceptions import ProblemException
from statsd import StatsClient

from nlp_annotator_api.annotators.SimpleTextGeographyAnnotator import SimpleTextGeographyAnnotator
from nlp_annotator_api.annotators.TextTableGeographyAnnotator import TextTableGeographyAnnotator
from nlp_annotator_api.annotators.SimpleTextClassifier import SimpleTextClassifier

## If you have several annotators, import them all here in the same way,
## and put them in the following dictionary:
annotators = {
    'SimpleTextGeographyAnnotator': SimpleTextGeographyAnnotator(),
    'TextTableGeographyAnnotator': TextTableGeographyAnnotator(),
    'SimpleTextClassifier': SimpleTextClassifier(),
}
## No other changes are needed in this controller for your specific annotators

## Return the name of all annotators callable in this API
async def get_annotator_definitions():
    return list(annotators.keys())


async def run_nlp_annotator(annotator, body, request: aiohttp.web.Request):
    client: StatsClient = request.config_dict['statsd_client']

    with client.pipeline() as pip:
        operation = next(iter(body.keys()))

        if not (annotator in annotators):
            pip.incr(f"run_nlp_annotator.bad_annotator.{operation}.{annotator}.count")
            return connexion.problem(404, 'Not Found', f"Annotator {annotator!r} not found.")

        pip.incr(f"run_nlp_annotator.{operation}.{annotator}.count")

        with pip.timer(f"run_nlp_annotator.{operation}.{annotator}.time"):
            return _run_annotator(annotators[annotator], body)


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

        annot = ann_cls() ## Annotator instance of the selected class

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

        if features['entity_names']:
            result['entity_names'] = annot.get_entity_names()

        if features['relationship_names']:
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
