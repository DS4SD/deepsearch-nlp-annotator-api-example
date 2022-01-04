## Testing the Application Locally

With the default parameters, the application runs on http://localhost:5000/api/v1/annotators/. The next parameter is the annotator name. Thus the actual URL is http://localhost:5000/api/v1/annotators/SimpleTextGeographyAnnotator.

The application is exposing an interactive Swagger UI interface, which is reachable at http://localhost:5000/api/v1/ui/.


### Finding Entities in Text

You can test it as in the following example:
```sh
curl -X POST -H "Content-Type: application/json" -H  "Authorization: test 123"\
    -d '{"find_entities": {"object_type": "text", "entity_names": ["cities", "countries", "provincies"], "texts": ["New Delhi is the capital of India.", "Baden-Württemberg is a state of Germany."]}}' \
    http://localhost:5000/api/v1/annotators/SimpleTextGeographyAnnotator
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
        "cities", 
        "countries", 
        "provincies"      
    ],
    "texts": [
      "New Delhi is the capital of India.", 
      "Baden-Württemberg is a state of Germany."
      ]
  }
}
```

Response for this query:
```json
{
  "entities": [
    {"cities": [
       {"type": "cities", 
        "match": "Delhi", 
        "original": "Delhi", 
        "range": [4, 9]}, 
       {"type": "cities", 
        "match": "New Delhi", 
        "original": "New Delhi", 
        "range": [0, 9]}
      ], 
     "countries": [
       {"type": "countries", 
        "match": "India", 
        "original": "India", 
        "range": [28, 33]}
      ], 
     "provincies": [
       {"type": "provincies", 
        "match": "Delhi", 
        "original": "Delhi", 
        "range": [4, 9]}
      ]
    }, 
    {"cities": [], 
     "countries": [
       {"type": "countries", 
        "match": "Germany", 
        "original": "Germany", 
        "range": [32, 39]}
       ], 
     "provincies": [
       {"type": "provincies", 
       "match": "Baden-W\u00fcrttemberg", 
       "original": "Baden-W\u00fcrttemberg", 
       "range": [0, 17]}
      ]
    }
  ]
}
```

### Querying Annotator Capabilities

You can also query the capabilities of this annotator:
```sh
curl -X POST -H "Content-Type: application/json" -H  "Authorization: test 123"\
    -d '{"features": {"entity_names": true, "relationship_names": true, "property_names": true, "labels": true}}' \
    http://localhost:5000/api/v1/annotators/SimpleTextGeographyAnnotator
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

Expected response:
```json
{
  "entity_names": [
    "countries",
    "cities",
    "provincies"
  ],
  "relationship_names": [
    "cities-to-countries",
    "cities-to-provincies",
    "provincies-to-countries"
  ],
  "property_names": [],
  "supported_object_types": [
    "text",
    "tables"
  ],
  "labels": {
    "entities": [
      {
        "key": "countries",
        "description": "Names of countries"
      },
      {
        "key": "cities",
        "description": "Names of cities"
      },
      {
        "key": "provincies",
        "description": "Names of provinces, states, and similar units"
      }
    ],
    "relationships": [
      {
        "key": "cities-to-countries",
        "description": "In-sentence relationship between entities ('cities', 'countries')",
        "columns": [
          {
            "key": "cities",
            "entities": [
              "cities"
            ]
          },
          {
            "key": "countries",
            "entities": [
              "countries"
            ]
          }
        ]
      },
      {
        "key": "cities-to-provincies",
        "description": "In-sentence relationship between entities ('cities', 'provincies')",
        "columns": [
          {
            "key": "cities",
            "entities": [
              "cities"
            ]
          },
          {
            "key": "provincies",
            "entities": [
              "provincies"
            ]
          }
        ]
      },
      {
        "key": "provincies-to-countries",
        "description": "In-sentence relationship between entities ('provincies', 'countries')",
        "columns": [
          {
            "key": "provincies",
            "entities": [
              "provincies"
            ]
          },
          {
            "key": "countries",
            "entities": [
              "countries"
            ]
          }
        ]
      }
    ]
  }
}
```

### Finding Entities in Tables

This annotator also handles table objects. To test it locally, here is a request with a 1-cell table:
```sh
curl -X POST -H "Content-Type: application/json" -H  "Authorization: test 123"\
    -d '{"find_entities": {"object_type": "table", "entity_names": ["cities", "countries"], "tables": [[[{"bbox": [], "spans": [[0, 0]], "text": "Bern, Switzerland", "type": "col_header"}]]]}}' \
    http://localhost:5000/api/v1/annotators/TextTableGeographyAnnotator
```

### Finding Relationships

For finding relationships in a text, you have to provide both the text and
the entities as found by the entities annotator. Below is an example request
body, to be used with the same headers and URL as above: 
```json
{
  "find_relationships": {
    "texts": ["Lisbon is the capital and the largest city of Portugal"],
    "entities": [{
      "cities": [
        {
          "type": "cities",
          "match": "Lisbon",
          "original": "Lisbon",
          "range": [
            0,
            6
          ]
        }
      ],
      "countries": [
        {
          "type": "countries",
          "match": "Portugal",
          "original": "Portugal",
          "range": [
            46,
            54
          ]
        }
      ]
    }],
    "object_type": "text",
    "relationship_names": ["cities-to-countries"]
  }
}
```

Response. In the "data" part, the entities are not substituted in (the CPS UI will do that), but given by reference. E.g., "cities.0" is the first city, here Lisbon. 
```json
{
  "relationships": [
    {
      "cities-to-countries": {
        "header": [
          "i",
          "j",
          "weight",
          "source"
        ],
        "data": [
          [
            "cities.0",
            "countries.0",
            1,
            "entities"
          ]
        ]
      }
    }
  ]
}
```

### Classifying Texts
You can test the sample annotator as in the following example:
```
curl -X POST -H "Content-Type: application/json" -H  "Authorization: test 123"\
    -d '{"find_properties": {"object_type": "text", "property_names": ["length", "category"], "texts": ["Definition: Fruit are sweet edible products of plant blossoms.", "Apples grow on apple trees and grow after the beautiful apple blossoms were visited by bees. Most people like apples. Doctors and nutritionist recommend that we eat a lot of them.","Theorem 1: Apples are fruit","An example of healthiness is their Vitamin-C content."], "entities": [{}, {}, {}, {}]}}' \
    http://localhost:5000/api/v1/annotators/SimpleTextClassifier
```

Here is the request body in more readable format. 
* `object_type` is what you will pass, here text, not tables or images.
* With `property_names` you can restrict which classifications you want to get, if the annotator offers several types. If the list is empty, all possible classifications will be returned.
* `texts` is a list of sentences to annotate.

```json
{
  "find_properties": {
    "object_type": "text",
    "property_names": [
        "length"
    ],
    "texts": [
      "Definition: Fruit are sweet edible products of plant blossoms.",
      "Apples grow on apple trees and grow after the beautiful apple blossoms were visited by bees. Most people like apples. Doctors and nutritionist recommend that we eat a lot of them.",
      "Theorem 1: Apples are fruit",
      "An example of healthiness is their Vitamin-C content"
      ],
    "entities": [{}, {}, {}, {}]
  }
}
```

The response for this query is a list of 4 results, one for each input text. Each result contains the two classifications.
```json
{"properties": [
  {"length": {"value": "short"}}, 
  {"length": {"value": "middle"}},
  {"length": {"value": "short"}}, 
  {"length": {"value": "short"}}
]}
```
