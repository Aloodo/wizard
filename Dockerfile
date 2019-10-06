FROM jgoerzen/debian-base-security:stretch
ENV TERM linux
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install postgresql python3-pip libpq-dev sudo
RUN DEBIAN_FRONTEND=noninteractive apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /srv/wizard
COPY src/requirements.txt /srv/wizard
RUN pip3 install -r /srv/wizard/requirements.txt

COPY src/db_setup.sh data/db_dump.sql* /srv/wizard/
COPY src/pg_hba.conf /srv/wizard
COPY src/schema.sql /srv/wizard
RUN /srv/wizard/db_setup.sh
RUN service postgresql stop

ENTRYPOINT ["/bin/sh"]
