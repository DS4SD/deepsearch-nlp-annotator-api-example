
from abc import ABC, abstractmethod
from typing import Any

from nlp_annotator_api.annotators.AbstractAnnotator import AbstractAnnotator


class BaseTextRelationshipAnnotator(AbstractAnnotator):

    @abstractmethod
    def key(self) -> str:
        pass

    @abstractmethod
    def columns(self) -> list:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def annotate_relationships_text(self, text: str, entity_map: dict, relationship_name: str) -> dict:
        pass
