# WatsonHealthAnnotator API Example

For `WatsonHealthAnnotator` be compatible with more watson concepts the user needs to add them to the config file.
(On watson format and with a brief description, e.g:  `"umls.GeneOrGenome": "ACE2"`)

## How to use
Endpoint: http://localhost:5000/api/v1/annotators/WatsonHealthAnnotator.

Required header: `Authorization`: Value on config (auth.api_key)

### To list all entities available:
Note: For the annotator entities the Watson concepts are formatted to kebab case.
 
body:
```json
{
    "features": {
      "entity_names": true
    }
}
```

Response for this query:
```json
{
    "entity_names": [
        "umls-organism",
        "umls-amino-acid-peptide-or-protein",
        "umls-biologically-active-substance",
        "umls-organic-chemical",
        "umls-pharmacologic-substance",
        "umls-nucleic-acid-nucleoside-or-nucleotide",
        "umls-gene-or-genome",
        "umls-activity",
        "umls-molecular-function",
        "umls-virus",
        "umls-geographic-area",
        "umls-immunologic-factor",
        "umls-disease-or-syndrome",
        "umls-receptor",
        "umls-pathologic-function",
        "umls-natural-phenomenon-or-process",
        "umls-neoplastic-process",
        "icd10-code"
    ],
    "relationship_names": [],
    "property_names": [],
    "supported_object_types": [
        "text"
    ],
    "labels": []
}
```

### Annotate example
body:
```json
{
    "find_entities": {
        "object_type": "text",
        "entity_names": [
            "umls-neoplastic-process",
            "icd10-code"
        ],
        "texts": [
            "Patient has lung cancer, but did not smoke. CT scan shows tumor in left lung. She may consider chemotherapy as part of a treatment plan."
        ]
    }
}
```

Response for this query:
```json
{
    "entities": [
        {
            "umls-neoplastic-process": [
                {
                    "type": "umls-neoplastic-process",
                    "original": "lung cancer",
                    "match": "Primary malignant neoplasm of lung",
                    "range": [
                        12,
                        23
                    ]
                },
                {
                    "type": "umls-neoplastic-process",
                    "original": "lung cancer",
                    "match": "Carcinoma of lung",
                    "range": [
                        12,
                        23
                    ]
                },
                {
                    "type": "umls-neoplastic-process",
                    "original": "lung cancer",
                    "match": "Malignant neoplasm of lung",
                    "range": [
                        12,
                        23
                    ]
                },
                {
                    "type": "umls-neoplastic-process",
                    "original": "tumor in left lung",
                    "match": "Lung Neoplasms",
                    "range": [
                        58,
                        76
                    ]
                },
                {
                    "type": "umls-neoplastic-process",
                    "original": "tumor in left lung",
                    "match": "Primary malignant neoplasm of left lung",
                    "range": [
                        58,
                        76
                    ]
                },
                {
                    "type": "umls-neoplastic-process",
                    "original": "tumor",
                    "match": "Neoplasms",
                    "range": [
                        58,
                        63
                    ]
                }
            ],
            "icd10-code": [
                {
                    "type": "icd10-code",
                    "original": "lung cancer",
                    "match": "C34.9,C34.90",
                    "range": [
                        12,
                        23
                    ]
                },
                {
                    "type": "icd10-code",
                    "original": "tumor in left lung",
                    "match": "D38.1,D49.1",
                    "range": [
                        58,
                        76
                    ]
                },
                {
                    "type": "icd10-code",
                    "original": "tumor in left lung",
                    "match": "C34.12,C34.32,C34.92",
                    "range": [
                        58,
                        76
                    ]
                }
            ]
        }
    ]
}
```