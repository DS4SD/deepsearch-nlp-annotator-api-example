
from abc import ABC, abstractmethod
from typing import Any

class BaseTextRelationshipAnnotator(ABC):

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
