#!/bin/sh

set -e

# validations
if [[ -z "${JENKINS_URL}"  || -z "${JENKINS_USERNAME}" || -z "${JENKINS_TOKEN}" ]]; then
  echo -e "requiredenvironment variable not set, probably not running in jenkins CI. \n Exiting..."
  exit 1
fi

if [[  -z "$1" ]]; then
  echo -e "ERROR: Target Jenkins agent label(s) not provided, please provide this as the first and only argument.\nExiting..."
  exit 1
fi

# fecth the offline value for the label 
is_offline=$(curl -sS "${JENKINS_URL}label/${1}/api/json" \
--user "${JENKINS_USERNAME}:${JENKINS_TOKEN}" | \
jq '.offline')

if [[  $is_offline == 'true' ]]; then
  echo -e "ERROR: No nodes are online for the provided label : ${1} \nExiting..."
  exit 1
else
  echo -e "At least one of the nodes for the provided label: ${1} is online"
fi
