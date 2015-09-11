#!/bin/bash

cd $(dirname $(readlink -f "$0"))

if [ ! -f out ]; then
    mkfifo out
fi

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

for file in scripts/* ; do
    $file &
done

buildStatus() {
    echo building status
    cat outputs/* | tr '\n' ' ' | sed 's/$/\n/' > out
    echo built
}

buildStatus

while inotifywait outputs -e modify -e create ; do
    buildStatus
done
