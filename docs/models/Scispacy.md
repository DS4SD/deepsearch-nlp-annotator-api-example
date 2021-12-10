# ScispaCy annotator

The example API provides the `ScispacyBiomedAnnotator` annotator which invokes models from [ScispaCy](https://allenai.github.io/scispacy/).

ScispaCy has multiple models which are tuned for finding different entities. A full list is available on the page https://allenai.github.io/scispacy/.
When a model is enabled in the example API, its entities are available for the text annotations.

Note that some models might require a non-trivial amount of memory for loading and running. When enabling more models, make sure to increase the memory limits of your environment accordingly.


## Querying Annotator Capabilities
You can query the capabilities of this annotator:
```sh
curl -X POST -H "Content-Type: application/json" -H  "Authorization: test 123"\
    -d '{"features": {"entity_names": true, "relationship_names": true, "property_names": true, "labels": true}}' \
    http://localhost:5000/api/v1/annotators/ScispacyBiomedAnnotator
```

Body in nicer format:
```json
{
  "features": {
    "entity_names": true,
    "relationship_names": true,
    "property_names": true,
    "labels": true
  }
}
```

The output will show the list all the entity types of the scispacy models enabled in the annotator (see above). 


Expected response:
```json
{
  "entity_names": [
    "entity",
    "cell_line",
    "cell_type",
    "dna",
    "protein",
    "rna",
    "chemical",
    "disease"
  ],
  "relationship_names": [],
  "property_names": [],
  "supported_object_types": [
    "text",
    "table"
  ],
  "labels": {
    "entities": [
      {
        "key": "entity",
        "description": "ENTITY from en_core_sci_md model."
      },
      {
        "key": "cell_line",
        "description": "CELL_LINE from en_ner_jnlpba_md model."
      },
      {
        "key": "cell_type",
        "description": "CELL_TYPE from en_ner_jnlpba_md model."
      },
      {
        "key": "dna",
        "description": "DNA from en_ner_jnlpba_md model."
      },
      {
        "key": "protein",
        "description": "PROTEIN from en_ner_jnlpba_md model."
      },
      {
        "key": "rna",
        "description": "RNA from en_ner_jnlpba_md model."
      },
      {
        "key": "chemical",
        "description": "CHEMICAL from en_ner_bc5cdr_md model."
      },
      {
        "key": "disease",
        "description": "DISEASE from en_ner_bc5cdr_md model."
      }
    ],
    "relationships": [],
    "properties": []
  }
}
```


## Finding Entities in Text
You can test it as in the following example:
```sh
curl -X POST "http://localhost:5000/api/v1/annotators/ScispacyBiomedAnnotator" -H  "accept: application/json" -H  "Authorization: test 123" -H  "Content-Type: application/json" -d "{\"find_entities\":{\"object_type\":\"text\",\"entity_names\":[\"disease\",\"protein\",\"chemical\"],\"texts\":[\"Spinal and bulbar muscular atrophy (SBMA) is an inherited motor neuron disease caused by the expansion of a polyglutamine tract within the androgen receptor (AR). SBMA can be caused by this easily.\",\"Consult for laparoscopic gastric bypass.\"]}}"
```

Here is the request body in more readable format. 
* `object_type` is what you will pass, here text, not tables or images.
* With `entity_names` you can restrict which entities you want to get, if the annotator offers several types. If the list is empty, all possible entities will be returned.
* `texts` is a list of sentences to annotate.

```json
{
  "find_entities": {
    "object_type": "text",
    "entity_names": [
        "disease",
        "protein",
        "chemical"
    ],
    "texts": [
      "Spinal and bulbar muscular atrophy (SBMA) is an inherited motor neuron disease caused by the expansion of a polyglutamine tract within the androgen receptor (AR). SBMA can be caused by this easily.",
      "Consult for laparoscopic gastric bypass."
    ]
  }
}
```

Example results:
```json
{
  "entities": [
    {
      "disease": [
        {
          "match": "Spinal and bulbar muscular atrophy",
          "original": "Spinal and bulbar muscular atrophy",
          "range": [
            0,
            34
          ],
          "type": "disease"
        },
        {
          "match": "SBMA",
          "original": "SBMA",
          "range": [
            36,
            40
          ],
          "type": "disease"
        },
        {
          "match": "polyglutamine tract",
          "original": "polyglutamine tract",
          "range": [
            108,
            127
          ],
          "type": "disease"
        },
        {
          "match": "SBMA",
          "original": "SBMA",
          "range": [
            163,
            167
          ],
          "type": "disease"
        }
      ],
      "protein": [
        {
          "match": "androgen receptor",
          "original": "androgen receptor",
          "range": [
            139,
            156
          ],
          "type": "protein"
        },
        {
          "match": "AR",
          "original": "AR",
          "range": [
            158,
            160
          ],
          "type": "protein"
        }
      ],
      "chemical": []
    },
    {
      "disease": [],
      "protein": [],
      "chemical": []
    }
  ]
}
```