#!/bin/bash
find . -maxdepth 1 -type d | sed -e 's/^\.[\/]*//' | xargs du -hs | sort -hr
