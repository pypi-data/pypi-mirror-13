#!/usr/bin/env bash

pushd `dirname $0` > /dev/null;
SCRIPTPATH=`pwd`;
popd > /dev/null


image_exists() {
    local image_search=$(docker images | tail -n +2 | awk '{print $1}' | grep "^$1$");
    if [ "$1" = "$image_search" ]; then
        local result=0
    else
        local result=1
    fi
    return $result
}

container_exists () {
    local container_search=$(docker ps -aq | xargs docker inspect --format '{{.Name}}' | grep "^/$1$");
    if [ "/$1" = "$container_search" ]; then
        local result=0
    else
        local result=1
    fi
    return $result
}


if container_exists mongo; then
    echo "mongodb container found. starting now."
    docker start mongo
else
    echo "mongodb container not found. setting up now."
    if ! $(image_exists tutum/mongodb); then
        echo "mongodb image not found.  pulling now."
        #docker pull mongo:3.1.8
        #TODO - switch to using the official mongo image
        #https://hub.docker.com/_/mongo/
        docker pull tutum/mongodb
    else
        echo "using existing mongodb image"
    fi;
    echo "creating mongodb container"
    docker run -d --name=mongo -e AUTH=no tutum/mongodb
    echo "mongodb container created"
fi


echo "building modjango image for testing"
if image_exists modjango; then
    echo "modjango image already exists"
else
    bash ./build.sh
fi

docker run -t -i \
    -v $SCRIPTPATH:/python_project \
    -p 80:80 \
    -p 443:443 \
    -e MONGO_URI=mongodb://mongodb \
    -e DJANGO_LOG_LEVEL=DEBUG \
    --link mongo:mongodb \
    modjango

