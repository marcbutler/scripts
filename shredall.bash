#!/bin/bash
if [ $# -ne 1 ] || [ ! -d "$1" ]; then
	echo "Usage: shredall dir"
	exit 1
fi

echo -n "Shredding..."
find -H "$1" -type f -print0 | xargs -0 shred -u
find -H "$1" -type d -delete
echo "done"
