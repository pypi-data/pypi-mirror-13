#!/usr/bin/env bash

pushd `dirname $0` > /dev/null;
SCRIPTPATH=`pwd`;
popd > /dev/null


docker build $* -t modjango $SCRIPTPATH
