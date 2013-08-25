#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: ${0##*/} file"
    exit 1
fi

tgt=${HOME}/conf/${1}
lnk=${HOME}/.${1}

if [ -e $lnk ]; then
    echo "$lnk - already exists"
    exit 1
fi

if [ ! -e $tgt ]; then
    echo "$tgt - no such file"
fi

ln -s $tgt $lnk
echo "$lnk - ok"
