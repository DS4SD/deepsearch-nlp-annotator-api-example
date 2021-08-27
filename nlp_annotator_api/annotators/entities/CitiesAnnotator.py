import os
from typing import Any, Optional
from .common.utils import resources_dir
from .common.DictionaryTextEntityAnnotator import DictionaryTextEntityAnnotator, Config


class CitiesAnnotator(DictionaryTextEntityAnnotator):
    
    def key(self) -> str:
        return "cities"

    def description(self) -> str:
        return "Names of cities"

    def __init__(self):
        super().__init__(
            Config(
                dictionary_filename=os.path.join(resources_dir, "cities.json")
            )
        )

