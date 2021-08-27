from .common.MultiEntitiesRelationshipAnnotator import MultiEntitiesRelationshipAnnotator, Config

from ..entities.CitiesAnnotator import CitiesAnnotator
from ..entities.ProvinciesAnnotator import ProvinciesAnnotator


class CitiesToProvinciesAnnotator(MultiEntitiesRelationshipAnnotator):

    def __init__(self):
        super().__init__(
            Config(
                entities=[CitiesAnnotator().key(), ProvinciesAnnotator().key()]
            )
        )
