#!/bin/bash

# Remove the temp copy of config file and return to the
# original directory on exit.
cleanup(){
        rm -f src/config.py
        popd
}
trap 'cleanup' EXIT

pushd $PWD &> /dev/null
cd $(dirname "$0")

dockerfail() {
	echo
	echo "Docker not found. Check that Docker is installed and running."
	echo 'See the "Getting Started" section of README.md for more info.'
	echo
	exit 1
}
docker ps &> /dev/null || dockerfail

set -e
set -x

pass config/wizard > src/config.py
docker build --tag=wizard_bot .

docker run \
	-p 5000:5000 \
	-e LC_ALL=C.UTF-8 \
	-e LANG=C.UTF-8 \
	--volume "$(pwd)"/src:/srv/wizard:ro,Z \
	--entrypoint="/usr/bin/env" wizard_bot python3 /srv/wizard/bot.py

