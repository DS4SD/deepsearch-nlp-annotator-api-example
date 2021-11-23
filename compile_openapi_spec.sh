#!/usr/bin/env bash

# LICENSED INTERNAL CODE. PROPERTY OF IBM.
# IBM Research Zurich Smart Annotator Licensed Internal Code
# (C) Copyright IBM Corp. 2019
# ALL RIGHTS RESERVED

# Creates or updates the the openapi definitions

set -e

swagger_cli_version=2.0.0

if ! hash npx 2>/dev/null; then
    echo "node and npx must be installed to generate the openapi-definition"
    exit 1
fi

if [[ ! -d node_modules ]]; then
  npm install swagger-cli@${swagger_cli_version}
fi

PATH=${PATH}:node_modules/.bin

echo "Bundling Swagger 2.0 definitions..."

swagger-cli validate ./nlp_annotator_api/resources/schemas/openapi.yaml
swagger-cli bundle -o ./openapi/bundled.json ./nlp_annotator_api/resources/schemas/openapi.yaml
