# IBM Corpus Processing Service
# (C) Copyright IBM Corporation 2019, 2021
# ALL RIGHTS RESERVED

## Run from .. as python3 -m tests.AnnotatorTest
## (Then it will have __name__ == "__main__", but so far it doesn't matter.)

import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('AnnotatorTest')
import pprint
#import os
#import sys

print("=============== Test start ===================")

def test_one_annotator(anno):

    sentences = [
        "Bern is the capital of Switzerland",
        "New Delhi is the capital of India.",
        "Sachsen and Baden-Württemberg are states of Germany."
        ]
    print("Sentences : ")
    for sen in sentences:
        print("  ", sen)

    print("---- First version, input entity list 'None', all entity types should be found: ----")
    all_entities = anno.annotate_batched_entities("text", sentences, None)
    all_relations = anno.annotate_batched_relationships(sentences, all_entities, None)
    for i, sentence in enumerate(sentences):
        print("OUTPUT FOR '" + sentence + "':")
        pprint.pprint(all_entities[i], indent = 2)
        pprint.pprint(all_relations[i], indent = 2)

    print("---- Second version, input entity list 'cities', 'countries', 'something_else' ----")
    all_entities = anno.annotate_batched_entities("text", sentences, ["cities", "countries", "something_else"])
    for i, sentence in enumerate(sentences):
        print("ENTITY OUTPUT FOR '" + sentence + "':")
        pprint.pprint(all_entities[i], indent = 2)

    print("---- Third version, input entity list 'something_else', result should be empty. ----")
    all_entities = anno.annotate_batched_entities("text", sentences, "something_else")
    for i, sentence in enumerate(sentences):
        print("ENTITY OUTPUT FOR '" + sentence + "':")
        pprint.pprint(all_entities[i], indent = 2)



from nlp_annotator_api.annotators.TextTableGeographyAnnotator import TextTableGeographyAnnotator as Annot
anno = Annot()
print("=====--------Test start with TextTableGeographyAnnotator -------======")
test_one_annotator(anno)

## More annotators here if present.

