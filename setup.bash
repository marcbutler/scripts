#!/bin/bash
bin=${HOME}/bin
src=${PWD}
for f in *.bash; do
    if [ "$f" == "setup.bash" ]; then
	continue
    fi
    x=${f%%.*}
    if [ ! -e $bin/$x ]; then
	ln -s $src/$f $bin/$x
    fi
done
