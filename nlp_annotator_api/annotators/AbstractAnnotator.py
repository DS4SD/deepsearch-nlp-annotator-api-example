from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses_json.api import DataClassJsonMixin


@dataclass
class AnnotatorMetadata(DataClassJsonMixin):
    name: str
    version: str
    url: str
    author: str
    description: str


class AbstractAnnotator(ABC):
    @staticmethod
    def annotator_metadata(parameters=None) -> AnnotatorMetadata:
        return AnnotatorMetadata(
            name="DeepSearch NLP Annotator API Example",
            version="1.1.0",
            url="https://github.com/IBM/deepsearch-nlp-annotator-api-example",
            author="IBM Research Europe – DeepSearch team",
            description="This annotator is an example usage of dictionaries and open pre-trained models integrating with the DeepSearch CPS platform."
        )
