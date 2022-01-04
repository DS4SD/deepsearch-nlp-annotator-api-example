# Geography Annotator 

## Implementation

The `SimpleTextGeographyAnnotator` implements a simple dictionary lookup via the [resource-files](./nlp_annotator_api/resources/)

## Entities and Relations

The following entities are exposed:

| Entity name  | Description |
| ------------ | ----------- |
| `cities` | Match with the cities dictionary |
| `provincies` | Provinces, states, etc. matching the provincies dictionary |
| `countries` | Match with the countries dictionary |

The following relationships are exposed:

| Relationship name  | Description |
| ------------ | ----------- |
| `cities-to-countries` | Relationship between the matched cities and countries. |
| `cities-to-provincies` | Relationship between the matched cities and provincies.  |
| `provincies-to-countries` | Relationship between the matched provincies and countries. |

The following properties are exposed in the small example (without actual AI models):

| Property name  | Description |
| ------------ | ----------- |
| `length` | Length of provided text (paragraph, table cell etc.) classified as small, middle, or long |

