#!/bin/bash
set -e
TAG=${1:-latest}
docker build --platform linux/amd64 -t h4x3rotab/llm-sandbox:$TAG .
docker push h4x3rotab/llm-sandbox:$TAG
[ "$TAG" != "latest" ] && docker tag h4x3rotab/llm-sandbox:$TAG h4x3rotab/llm-sandbox:latest && docker push h4x3rotab/llm-sandbox:latest