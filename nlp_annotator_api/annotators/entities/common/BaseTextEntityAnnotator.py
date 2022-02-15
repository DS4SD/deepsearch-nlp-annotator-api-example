
from abc import ABC, abstractmethod
from typing import Any, Optional

from nlp_annotator_api.annotators.AbstractAnnotator import AbstractAnnotator


class BaseTextEntityAnnotator(AbstractAnnotator):

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
