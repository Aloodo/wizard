#!/bin/bash

set -e
set -x

# Run this script from inside its own directory
trap popd EXIT
pushd $PWD
cd $(dirname "$0")

# Application config file. (Overwrite the version used
# for testing in a container)
mv conf/config.py .

if [ "x$1" != "xq" ] ; then
	apt-get update
	apt-get -y install certbot python-certbot-apache postgresql python3-pip apache2 libapache2-mod-wsgi-py3 libpq-dev
	pip3 install -r requirements.txt
fi

# Crontab entries
# chown root.root conf/cron/*/*
# chmod 755 conf/cron/*/*
# cp -p conf/cron/daily/* /etc/cron.daily
# cp -p conf/cron/weekly/* /etc/cron.weekly

# Config file for WSGI on the web server
cp conf/wsgi.conf /etc/apache2/conf-available
a2enmod wsgi
a2enconf wsgi

# Set up the database (same as in the container). Web
# server should be down when database is being worked on.
if [ "x$1" != "xq" ] ; then
	systemctl stop apache2
	./db_setup.sh
fi

# Finally restart the web server
systemctl restart apache2
