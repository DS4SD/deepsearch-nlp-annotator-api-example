from .common.MultiEntitiesRelationshipAnnotator import MultiEntitiesRelationshipAnnotator, Config

from ..entities.CitiesAnnotator import CitiesAnnotator
from ..entities.CountriesAnnotator import CountriesAnnotator


class CitiesToCountriesAnnotator(MultiEntitiesRelationshipAnnotator):

    def __init__(self):
        super().__init__(
            Config(
                entities=[CitiesAnnotator().key(), CountriesAnnotator().key()]
            )
        )
