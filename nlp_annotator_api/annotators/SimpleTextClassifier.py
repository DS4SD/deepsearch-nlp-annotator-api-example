# IBM Corpus Processing Service
# (C) Copyright IBM Corporation 2019, 2021
# ALL RIGHTS RESERVED

## Sample External API Annotator
## Apart from initialization of provided entities and model loading,
## the only function you really have to change here is "annotate_entities_text".

import logging
logger = logging.getLogger('cps-nlp')
from typing import List, Optional
#import pprint ## For debugging only.

from .properties.TextLengthAnnotator import TextLengthAnnotator


class SimpleTextClassifier:
    ## This is the class name that you need to use in the controller.

    supports = ('text', )

    _props_annotator_classes = [
        TextLengthAnnotator,
    ]

    def __init__(self):

        self._props_annots = {}
        self._initialize_annotators()

        self.entity_names = [] # This annotator has no entities
        self.relationship_names = [] # This annotator has no relationships
        self.property_names = list(self._props_annots.keys())
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
        # Dummy entity labels
        entities_with_desc = []
        # Dummy relationships labels
        relationships_with_columns = []

        # Derive property labels from classes   
        properties_with_desc = [
            {
                "key": annot.key(), 
                "description": annot.description()
            }
            for annot in self._props_annots.values()
        ]


        return {
            'entities': entities_with_desc,
            'relationships': relationships_with_columns,
            'properties': properties_with_desc
        }

    def _initialize_annotators(self):

        # Initialize dict of annotator instances `self._rel_annots`
        for cls in self._props_annotator_classes:
            annot = cls()
            self._props_annots[annot.key()] = annot

    # def annotate_batched_entities(self, object_type, items: List, entity_names: Optional[List[str]]) -> List[dict]:
    #     return [[] for _ in items]

    def annotate_batched_properties(self, texts: List[str], entities: List[dict], property_names: Optional[List[str]]) -> List[dict]:
        if property_names is None:
            # This means that the user did not explicitly specify which properties they want.
            # So, assume our list.
            desired_properties = self.property_names
        else:
            desired_properties = [property for property in property_names if property in self.property_names]
        results = []

        # Loop over the text snippets and classify them, output per text should be of this form:
        #    {"property-name": {"value":  "short"} }

        for text in texts:
            ## Length classification
            properties = {}
            for property_name in desired_properties:
                properties[property_name] = self._props_annots[property_name].annotate_properties_text(text)

            results.append(properties)

        return results
