#!/bin/bash

fail() {
	echo $*
	exit 1
}

docker ps &> /dev/null || fail "Docker not installed or not running."

# Remove anything not tagged "debian"
echo -n "Cleaning up Docker images: "
docker image ls | grep -v debian | awk 'NR>1 {print $3}' | xargs docker rmi -f 2> /dev/null | grep "^Deleted" | wc -l

# prune all files that are now unused
docker system prune

echo
echo "Remaining Docker images"
docker image ls
