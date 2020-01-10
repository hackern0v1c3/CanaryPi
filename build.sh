#!/bin/bash

# https://github.com/docker/buildx

# Notes on setting up build environment on linux
# https://github.com/docker/buildx/issues/57
# The easiest way to setup qemu should be to run docker run --privileged linuxkit/binfmt:v0.7

usage()
{
    echo "This script will push canarypi to dockerhub using a specific version number and update latest tag."
    echo "Images will be built for linux/arm64,linux/amd64, and linux/arm/v7"
    echo "A version must be specified"
    echo "Usage: $0 -v x.x"
}

if [ "$1" == "" ]; then
    usage
    exit
fi

push()
{
    if [ "$version" == "" ]; then
        usage
        exit
    fi

    # Create BuildKit
    docker buildx create --name canarypi --platform linux/arm64,linux/amd64,linux/arm/v7
    docker buildx use canarypi

    # Build multi-platform images
    docker buildx build --no-cache --platform linux/arm64,linux/amd64,linux/arm/v7 -t macmondev/canarypi:$version --push .
    docker buildx build --no-cache --platform linux/arm64,linux/amd64,linux/arm/v7 -t macmondev/canarypi --push .

    # echo ==== \$ docker buildx imagetools inspect macmondev/canarypi:0.1
    docker buildx imagetools inspect macmondev/canarypi

    docker buildx stop canarypi
    docker buildx rm canarypi
}

# Main
while [ "$1" != "" ]; do
    case $1 in
        -v | --version )    shift
                            version=$1
                            push
                            exit
                            ;;
        -h | --help )       usage
                            exit
                            ;;
        * )                 usage
                            exit 1
    esac
    shift
done