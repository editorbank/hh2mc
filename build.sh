#!/bin/env bash
source $(dirname $0)/config.sh

[ ! -f hh2mc.bin ] && ./py2bin.sh ./hh2mc.py 

[ ! -z "$($docker ps -q -a -f name=$docker_container)" ] && $docker rm -f $docker_container
[ ! -z "$($docker images -q -f reference=$docker_image)" ] && $docker rmi -f $docker_image

$docker build --tag $docker_image $dockerfile_dir
$docker run -it --rm --name $docker_container $docker_image /hh2mc.bin --help
