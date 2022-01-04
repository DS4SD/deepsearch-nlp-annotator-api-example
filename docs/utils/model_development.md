## Develop a new annotator

### Code structure

```
./chart                             # the Helm chart needed for the cluster deployment
./nlp_annotator_api
./nlp_annotator_api/annotators/     # the models implementing the entity, relationships and properties annotators
./nlp_annotator_api/resources/      # resource files used by the /annotators/ (e.g. JSON dictionaries)
./nlp_annotator_api/server/         # the API serving the models in /annotators/ 
```

### New annotators

For adding a new annotator, follow these steps:

1. Add your annotator class in the folder `./nlp_annotator_api/annotators/`. (the other example annotator could be helpful to identify the minimum interface)

2. Add the annotator to the controller factory in `./nlp_annotator_api/server/controllers/annotate_controller.py`

    ```py
    annotators = {
        'SimpleTextGeographyAnnotator': SimpleTextGeographyAnnotator(),
        'TextTableGeographyAnnotator': TextTableGeographyAnnotator(),
        'SimpleTextClassifier': SimpleTextClassifier(),
    }
    ```

