
from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseTextEntityAnnotator(ABC):

    @abstractmethod
    def key(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    def initialize(self):
        return

    @abstractmethod
    def annotate_entities_text(self, text: str) -> list:
        pass
