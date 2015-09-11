#!/bin/bash

cd $(dirname $(readlink -f "$0"))

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

find scripts -executable ! -type d -exec sh -c '"$0" &' {} \;

buildStatus() {
    cat outputs/* | tr '\n' ' ' | sed 's/$/\n/' 
}

buildStatus

while inotifywait outputs -e modify -e create 1>/dev/null 2>/dev/null ; do
    buildStatus
done
