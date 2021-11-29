# LICENSED INTERNAL CODE. PROPERTY OF IBM.
# IBM Research Zurich Smart Annotator Licensed Internal Code
# (C) Copyright IBM Corp. 2017
# ALL RIGHTS RESERVED

import logging
from typing import Optional, List, Dict

import spacy

logger = logging.getLogger('cps-nlp')

EntityMap = Dict[str, List[dict]]


## model               F1     Entity Types
# en_ner_craft_md      76.11   GGP, SO, TAXON, CHEBI, GO, CL
# en_ner_jnlpba_md     71.62   DNA, CELL_TYPE, CELL_LINE, RNA, PROTEIN
# en_ner_bc5cdr_md     84.49   DISEASE, CHEMICAL
# en_ner_bionlp13cg_md 77.75   AMINO_ACID, ANATOMICAL_SYSTEM, CANCER, CELL, CELLULAR_COMPONENT, DEVELOPING_ANATOMICAL_STRUCTURE, GENE_OR_GENE_PRODUCT, IMMATERIAL_ANATOMICAL_ENTITY, MULTI-TISSUE_STRUCTURE, ORGAN, ORGANISM, ORGANISM_SUBDIVISION, ORGANISM_SUBSTANCE, PATHOLOGICAL_FORMATION, SIMPLE_CHEMICAL, TISSUE


# Models enabled in this list must also be installed.
# See requirements.txt for the corresponding packages.
_models = ['en_core_sci_md',
           #'en_ner_craft_md',
           'en_ner_jnlpba_md',
           'en_ner_bc5cdr_md',
           #'en_ner_bionlp13cg_md'
]


class ScispacyBiomedAnnotator:

    supports = ('text', 'table', )


    def __init__(self, config=None):
        if config is None:
            config = {}

        self.initialize()

    def initialize(self):
        self.nlps = [ spacy.load(model) for model in _models ]

        self.ent_to_models = {}
        self.labels = {
            'entities': [],
            'relationships': [],
            'properties': [],
        }
        self.relationship_names = []
        self.property_names = []
        for model_ix, model in enumerate(self.nlps):
            for entity_name in model.pipe_labels.get('ner', []):
                self.labels['entities'].append({
                    'key': entity_name.lower(),
                    'description': f'{entity_name} from {_models[model_ix]} model.',
                })
                self.ent_to_models[entity_name.lower()] = model_ix

        self.entity_names = [item['key'] for item in self.labels['entities']]
        self.relationship_names = [item['key'] for item in self.labels['relationships']]
        self.property_names = [item['key'] for item in self.labels['properties']]


    def get_entity_names(self):
        return self.entity_names

    def get_relationship_names(self):
        return self.relationship_names

    def get_property_names(self):
        return self.property_names

    def get_labels(self):
        return self.labels

    def annotate_with_spacy(self, text, nlps):
        matches = []
        for nlp_i, nlp in enumerate(nlps):
            logger.debug("Running model %s of %s", nlp_i, len(nlps))
            doc = nlp(text)
            for ent in doc.ents:
                tmp = {
                    "match" : ent.text,
                    "original": text[ent.start_char:ent.end_char],
                    "range" : [ent.start_char,ent.end_char],
                    "type"  : ent.label_.lower()
                }
                matches.append(tmp)
        return matches

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
        ## Identify which models should be executed to produce the entities
        selected_models_ix = set([self.ent_to_models[ent_name] for ent_name in desired_entities])
        selected_nlps = [self.nlps[ix] for ix in selected_models_ix]

        ## Annotate one item with the desired entities.
        ## Output: List of entities in CPS format, different for text, table, or images
        if object_type == "text":
            all_matched_entities = self.annotate_with_spacy(item, selected_nlps)
            matched_entities = [ent for ent in all_matched_entities if ent['type'] in desired_entities]
            return matched_entities
        elif object_type == "table":
            return self.annotate_entities_table(item, desired_entities)
        ## By the validation code in 'annotate_controller.py' no other object_type can get here. 

    def annotate_entities_table(self, table: List[List[dict]], desired_entities: List[str]) -> list:
        ## Annotate one table with the desired entities.
        ## Output: List of entities in CPS format for table entities.

        ## This annotator annotates cell texts individually, using the text annotator.
        ## Only if you want something more complex, you need to change something here.

        # print("------ Starting 'annotate_entities_table' -------")
        # print("-------with this table: ")
        # print(table)
        table_entities = []
        for i, row in enumerate(table):
            for j, cell in enumerate(row): 
                text_entities = self.annotate_entities("text", cell["text"], desired_entities)
                ## Extend from text-entity CPS format with fields type, match, original, range 
                #  to table-entity CPS format, which looks like this:
                # {
                #     "cell_type": "body",
                #     "coords": [[ 1, 0]], ## Coordinates of the cell within the table, here row 1, cell 0
                #     "match": "Amsterdam",
                #     "original": "Amsterdam",
                #     "prov": "data",
                #     "range": [0, 10 ], ## Start character and end+1 of match within cell
                #     "source_field": "data",
                #     "source_field_type": "table",
                #     "type": "cities"
                # },
                for entity in text_entities:
                    entity["cell_type"] = cell["type"]
                    entity["coords"] = cell["spans"]
                    entity["prov"] = "data"
                    entity["source_field"] = "data"
                    entity["source_field_type"] = "table"
                    table_entities.append(entity)
        #print("Table entities returned from 'annotate_entities_table': ")
        #pprint.pprint(table_entities)  
        return table_entities
