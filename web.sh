#!/bin/bash

DATASOURCE=wizard@wizard.aloodo.org

trap popd EXIT
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
ssh $DATASOURCE true || echo "Can't connect to $DATASOURCE"

mkdir -p data
ssh $DATASOURCE pg_dump --user postgres wizard > data/db_dump.sql || echo "Failed to get live data from $DATASOURCE"

set -e
set -x

docker build --tag=wizard_web .

docker run \
	-p 5000:5000 \
	-e FLASK_APP=/srv/wizard/webapp.py \
	-e FLASK_ENV=development \
	-e LC_ALL=C.UTF-8 \
	-e LANG=C.UTF-8 \
	--volume "$(pwd)"/src:/srv/wizard:ro,Z \
	--entrypoint="/usr/local/bin/flask" wizard_web run --host=0.0.0.0
