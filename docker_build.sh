#!/bin/bash

source .builder.conf

set -e

docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .