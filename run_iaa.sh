#!/bin/bash
if [[ -n $1 ]]; then
  CMD="$@"
else
  CMD=bash
fi
docker-compose run --user root iaa_service $CMD
