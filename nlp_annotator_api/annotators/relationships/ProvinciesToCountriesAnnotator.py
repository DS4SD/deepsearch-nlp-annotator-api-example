from .common.MultiEntitiesRelationshipAnnotator import MultiEntitiesRelationshipAnnotator, Config

from ..entities.CountriesAnnotator import CountriesAnnotator
from ..entities.ProvinciesAnnotator import ProvinciesAnnotator


class ProvinciesToCountriesAnnotator(MultiEntitiesRelationshipAnnotator):

    def __init__(self):
        super().__init__(
            Config(
                entities=[ProvinciesAnnotator().key(), CountriesAnnotator().key()]
            )
        )
