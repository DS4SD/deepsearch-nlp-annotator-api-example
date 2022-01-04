# DeepSearch NLP Annotator API Example

This repository contains a simple annotator fulfilling the interface required
by CPS. It is meant to be cloned, and then adapted to specific models. 

## Example models

In terms of functionality, the current code implements several different
models, ranging from very simple (dictionary look-ups) to more SOTA (spaCy-models).

These models are:

- [SimpleTextGeographyAnnotator](./docs/models/SimpleTextGeography.md)
- [ScispacyBiomedAnnotator](./docs/models/Scispacy.md)
- [WatsonHealthAnnotator](./docs/models/WatsonHealthAnnotator.md)

## Install

To install the dependencies, execute the following commands in the
`deepsearch-nlp-annotator-api-example` folder 

```sh
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Run API server

To launch the Rest-API server, execute the following command

```sh
sh launch_server.sh
```

The application is exposing an interactive Swagger UI interface, which is
reachable at http://localhost:5000/api/v1/ui/. By default the API requires
`test 123` as authentication (see green `Authorize` button on right top corner).

## Query API server

A detailed description to query the Rest-API can be found [here](./docs/utils/query.md). We
also have an easy `interactive` query script, which allows you to read strings from a txt-file
and visualise the output. For that, first launch the server (see above) and then go to the
`tests` folder and execute,

```sh
python interactive_test.py
```

By default, it will read line-by-line a [TXT file](./tests/data/geography). In case you want to run
it on other TXT files, simply type

```sh
python interactive_test.py --filename <path-to-text-file>
```

In case you want to run on CCS document files, simply type

```sh
python interactive_test.py --documents <directory-with-CCS-converted-doc's>
```

## Further details

- [Running the Annotator Application through Curl](./docs/utils/query.md)
    - How to launch locally
    - Example input and output
- [Use the Annotator in CPS](./docs/utils/cps.md)
    - How to configure the model in CPS
- [Using an Ngrok Tunnel](./docs/utils/ngrok.md)
    - Example of local development connected to CPS
- [Deploying the application](./docs/utils/deploy.md)
    - How to deploy for production usage
- [Develop a new annotator](./docs/utils/model_development.md)
    - How to add your own annotator

