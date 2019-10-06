#!/bin/bash

set -e
set -x

trap popd EXIT
pushd $PWD
cd $(dirname "$0")

cp pg_hba.conf /etc/postgresql/9.6/main
service postgresql start

# create the database if it does not exist already
echo "SELECT 'CREATE DATABASE wizard' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'wizard')\gexec" | psql --user postgres

[ -e db_dump.sql ] && psql --user postgres wizard < db_dump.sql
psql --user postgres -d wizard -f schema.sql

