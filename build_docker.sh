#!/bin/bash
# Tim H 2023
# Builds and runs a docker image 

# https://chrisedrego.medium.com/20-best-practise-in-2020-for-dockerfile-bb04104bffb6

set -e
clear

# brew install hadolint

export DOCKER_HUB_USERNAME="themolecularman"
export DOCKER_REPO_NAME="verizon-lte-extender-reboot"

# Launch docker if it is not already running
# have to wait for it to finish loading
open -a Docker
# && sleep 10

# check the lint syntax of the docker file before building it
# will bail if significant problems are found
# hadolint Dockerfile --failure-threshold warning

# can't skip this step
docker pull alpine:3.17.3

#########################
# Multi-platform build
#########################
# https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/

# see which platforms are supported with Docker Desktop
# docker buildx ls

# create a docker container that will allow multi-arch building
# only have to do this once
# https://forums.docker.com/t/error-multiple-platforms-feature-is-currently-not-supported-for-docker-driver/124811/11
# docker buildx create --name multiarch --driver docker-container --use
# now run this again to see the newly supported archs
# docker buildx ls
# list all available architectures
# docker buildx ls | grep arm | cut -c63- | tr , '\n' | sort --unique
# view the local system's architecture:
# sudo docker info | grep Architecture

# MULTI-ARCHITECTURE VERSION
# export DOCKER_TAG_NAME="multiarch"
# docker buildx build \
#     --push \
#     --platform linux/amd64 \
#     --tag "$DOCKER_HUB_USERNAME/$DOCKER_REPO_NAME:$DOCKER_TAG_NAME" .

# single architecture (x86_64) build process for Apple M1:
export DOCKER_TAG_NAME="latest"
docker build -t "$DOCKER_REPO_NAME" .
# docker tag "$DOCKER_REPO_NAME" "$DOCKER_HUB_USERNAME/$DOCKER_REPO_NAME:$DOCKER_TAG_NAME"
# docker push "$DOCKER_HUB_USERNAME/$DOCKER_REPO_NAME"

# docker compose up
# debug cleanup - delete
# sudo docker container stop "$NEW_CONTAINER_ID"
# sudo docker container rm "$NEW_CONTAINER_ID"

echo "[build_docker.sh] bash script finished successfully"
