import os
from typing import Any, Optional
from .common.utils import resources_dir
from .common.DictionaryTextEntityAnnotator import DictionaryTextEntityAnnotator, Config


class ProvinciesAnnotator(DictionaryTextEntityAnnotator):
    
    def key(self) -> str:
        return "provincies"

    def description(self) -> str:
        return "Names of provinces, states, and similar units"

    def __init__(self):
        super().__init__(
            Config(
                dictionary_filename=os.path.join(resources_dir, "provincies.json")
            )
        )
