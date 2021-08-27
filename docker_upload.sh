#!/bin/bash
source .builder.conf

DOCKER_TMP_TAG=${TMP_IMAGE_TAG:-dev}
DOCKER_REGISTRY_LOGIN=${DOCKER_REGISTRY_LOGIN}
DOCKER_REGISTRY_PWD=${DOCKER_REGISTRY_PWD}

set -e

# Jenkins
if [ -n "$JENKINS_BRANCH" ]; then
    DOCKER_TAG=${JENKINS_BRANCH}
    DOCKER_COMMIT_TAG=${DOCKER_TAG}-$(cat .docker.tag)

    if [ -n "$PR_NUMBER" ]; then
        PR_DOCKER_TAG="PR-${PR_NUMBER}"
        docker tag ${DOCKER_IMAGE}:${DOCKER_TMP_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${PR_DOCKER_TAG}
        docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${PR_DOCKER_TAG}
        exit 0
    fi


# Travis
elif [ "$TRAVIS" == "true" ]; then
    DOCKER_TAG=travis_${TRAVIS_BRANCH}
    DOCKER_COMMIT_TAG=${DOCKER_TAG}-$(echo ${TRAVIS_COMMIT} | head -c 7)-$(date +%Y%m%d%H%M%S)
    GIT_COMMIT=${TRAVIS_COMMIT:-000000}

    if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then
        echo "No upload on pull requests"
        exit
    fi

else
    DOCKER_COMMIT_TAG=${DOCKER_TAG}-$(git rev-parse --short HEAD)-$(date +%Y%m%d%H%M%S)
fi

DOCKER_BRANCH_TAG=${DOCKER_TAG}
for tag in $DOCKER_BRANCH_TAG $DOCKER_COMMIT_TAG; do
    echo "Tagging $tag"
    docker tag ${DOCKER_IMAGE}:${DOCKER_TMP_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${tag}
    docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${tag}
    echo "${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${tag}" > .docker.url
done

# Exclusion of PR built image from artifactory must be executed after a successfull master/tag branch.

PR_DOCKER_TAG="PR-$(git log -1 --oneline | sed -n 's/.*#\([0-9]*\).*/\1/p')"
if [[ $PR_DOCKER_TAG =~ [0-9]+$ ]]; then
    echo "Erasing ${DOCKER_IMAGE}/${PR_DOCKER_TAG} image from artifactory"
    curl -u$DOCKER_REGISTRY_LOGIN:$DOCKER_REGISTRY_PWD -X DELETE "https://${DOCKER_REGISTRY}/artifactory/zrl-sa-docker-local/${DOCKER_IMAGE}/${PR_DOCKER_TAG}"
fi

docker rmi ${DOCKER_IMAGE}:${DOCKER_TMP_TAG}
