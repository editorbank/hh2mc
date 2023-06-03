#!/bin/env bash
source $(dirname $0)/config.sh

[ ! -z "$($docker ps -q -a -f name=$docker_container)" ] && $docker rm -f $docker_container
[ ! -z "$($docker images -q -f reference=$docker_image)" ] && $docker rmi -f $docker_image

for i in $(git ls-files --others --ignored --exclude-standard|grep -v .bak); do
  rm -v $i
done

