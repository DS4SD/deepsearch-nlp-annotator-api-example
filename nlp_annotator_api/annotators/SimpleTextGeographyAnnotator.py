# IBM Corpus Processing Service
# (C) Copyright IBM Corporation 2019, 2021
# ALL RIGHTS RESERVED

## Sample External API Annotator
## Apart from initialization of provided entities and model loading,
## the only function you really have to change here is "annotate_entities_text".

import logging

from .AbstractAnnotator import AbstractAnnotator

logger = logging.getLogger('cps-nlp')
from typing import List, Optional
#import pprint ## For debugging only.

from .entities.CitiesAnnotator import CitiesAnnotator
from .entities.CountriesAnnotator import CountriesAnnotator
from .entities.ProvinciesAnnotator import ProvinciesAnnotator

from .relationships.CitiesToCountriesAnnotator import CitiesToCountriesAnnotator
from .relationships.CitiesToProvinciesAnnotator import CitiesToProvinciesAnnotator
from .relationships.ProvinciesToCountriesAnnotator import ProvinciesToCountriesAnnotator


class SimpleTextGeographyAnnotator(AbstractAnnotator):
    ## This is the class name that you need to use in the controller.

    supports = ('text', )

    _ent_annotator_classes = [
        CitiesAnnotator,
        CountriesAnnotator,
        ProvinciesAnnotator,
    ]

    _rel_annotator_classes = [
        CitiesToCountriesAnnotator,
        CitiesToProvinciesAnnotator,
        ProvinciesToCountriesAnnotator,
    ]

    def __init__(self):

        self._ent_annots = {}
        self._rel_annots = {}
        self._initialize_annotators()

        self.entity_names = list(self._ent_annots.keys())
        self.relationship_names = list(self._rel_annots.keys())
        self.property_names = [] # This example annotator does not have any property annotator
        self.labels = self._generate_annotator_labels()

    def get_entity_names(self):
        return self.entity_names

    def get_relationship_names(self):
        return self.relationship_names

    def get_property_names(self):
        return self.property_names

    def get_labels(self):
        return self.labels

    def _generate_annotator_labels(self):
        # Derive entity labels from classes    
        entities_with_desc = [
            {
                "key": annot.key(), 
                "description": annot.description()
            }
            for annot in self._ent_annots.values()
        ]
        # Dummy implementation of property labels    
        property_names = self.get_property_names()
        properties_with_desc = [{"key": property, "description": f"Property of type {property!r}"} for property in property_names]

        # Derive relationships labels from classes
        relationships_with_columns = [
            {
                "key": annot.key(),
                "description": annot.description(),
                "columns": annot.columns()
            }
            for annot in self._rel_annots.values()
        ]

        return {
            'entities': entities_with_desc,
            'relationships': relationships_with_columns,
            'properties': properties_with_desc
        }

    def _initialize_annotators(self):
        # Initialize dict of annotator instances `self._ent_annots`
        for cls in self._ent_annotator_classes:
            annot = cls()
            self._ent_annots[annot.key()] = annot

        # Initialize dict of annotator instances `self._rel_annots`
        for cls in self._rel_annotator_classes:
            annot = cls()
            self._rel_annots[annot.key()] = annot

    def annotate_batched_entities(self, object_type, items: List, entity_names: Optional[List[str]]) -> List[dict]:
        ## An item is a string if object_type == "text", and List[List[dict]] if object_type == "table"
        if entity_names is None:
            # This means that the user did not explicitly specify which entities they want.
            # So, assume our list.
            desired_entities = self.entity_names
        else:
            desired_entities = [entity for entity in entity_names if entity in self.entity_names]

        results = []

        ## Iterate over all items, provide all desired entities,
        ## and sort them by category.
        ## (Because many NER models provide multiple entities.)
        for item in items:
            entity_map = {}
            try:
                cps_entities = self.annotate_entities(object_type, item, desired_entities)
            except Exception as exc:
                cps_entities = []
                logger.exception("Error in annotator for object_type " + object_type
                                  + " with this content: " + str(item))
            for entity_name in desired_entities:
                entity_map[entity_name] = [entity for entity in cps_entities if entity["type"] == entity_name]
            results.append(entity_map)

        #print("Entities returned from 'annotate_batched_entities', for type " + object_type)
        #pprint.pprint(results)  

        return results

    def annotate_entities(self, object_type, item, desired_entities: List[str]) -> list:
        ## Annotate one item with the desired entities.
        ## Output: List of entities in CPS format, different for text, table, or images
        if object_type == "text":
            matched_entities = []
            for entity_name in desired_entities:
                matched_entities.extend(self._ent_annots[entity_name].annotate_entities_text(item))
            return matched_entities
        # elif object_type == "table":
        #     return self.annotate_entities_table(item, desired_entities)
        ## By the validation code in 'annotate_controller.py' no other object_type can get here. 


    def annotate_batched_relationships(self, texts: List[str], entities: List[dict], relationship_names: Optional[List[str]]) -> List[dict]:
        if relationship_names is None:
            # This means that the user did not explicitly specify which relationships they want.
            # So, assume our list.
            relationship_names = self.relationship_names

        results = []

        # Loop over the text snippets and the entities already matched in those
        for text, entity_map in zip(texts, entities):
            result = {}
            # Iterate over all relationships requested by the user
            for relation in relationship_names:
                if relation in self.relationship_names:
                    result[relation] = self._rel_annots[relation].annotate_relationships_text(text, entity_map)

            if result:
                results.append(result)

        return results
