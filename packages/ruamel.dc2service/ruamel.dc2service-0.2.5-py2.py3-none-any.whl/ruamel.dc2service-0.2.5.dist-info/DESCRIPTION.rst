==============
``dc2service``
==============

The ``dc2service`` utility generates configuration files for
``systemd``/``Upstart`` based on a single ``docker-compose`` YAML input file.

The init type is autodetected, but can be overruled from the commandline.

The service name is determinted by the ``container_name`` entries for all
the services in the YAML file. Each service  has to have a ``container_name``
specified.

As ``docker-compose`` YAML file format doesn't allow for extra metadata
fields, two comment entries at the beginning of the YAML file
are parsed for a description and author.

If external ports are specified (i.e. of the form "ip:ip") then the
external port numbers are extended to the description.

The file generation is template based and can easily be adjusted to your needs.
Their location can be viewed by doing ``dc2service templates``

Example input YAML file for Mongo DB
-------------------------------------------------------

``docker-compose.yml`` file for single service running Mongo DB with
an external (i.e. host oriented) port::

  # author: Anthon van der Neut <a.van.der.neut@ruamel.eu>
  # description: mongo container
  mongodb:
    container_name: mongo
    image: mongo:2.4
    volumes:
     - /data1/DB/mongo:/data/db
    ports:
    - 27017:27017

.. example code docker-compose.yml


``systemd``
-----------

The command ``dc2service --systemd generate /opt/docker/mongo/docker-compose.yml`` will
generate the file ``/etc/systemd/system/mongo-docker.service``::

  [Unit]
  Description=mongo container on port 27017
  # Author = Anthon van der Neut <a.van.der.neut@ruamel.eu> (dc2service 0.1.0.dev)
  Requires=docker.service
  After=docker.service

  [Service]
  Restart=always
  ExecStart=/opt/util/docker-compose/bin/docker-compose -f /opt/docker/mongo/docker-compose.yml up --no-recreate
  ExecStop=/opt/util/docker-compose/bin/docker-compose -f /opt/docker/mongo/docker-compose.yml stop

  [Install]
  WantedBy=multi-user.target

.. example code mongo-docker.service


Upstart
-------

The command ``dc2service --upstart generate /opt/docker/mongo/docker-compose.yml`` will
generate the file ``/etc/init/mongo-docker.conf``::

  description "mongo container on port 27017"
  author "Anthon van der Neut <a.van.der.neut@ruamel.eu> (dc2service 0.1.0.dev)"
  start on filesystem and started docker
  stop on runlevel [!2345]
  respawn

  pre-start script
    /opt/util/docker-compose/bin/docker-compose -f /opt/docker/mongo/docker-compose.yml up -d --no-recreate
  end script

  script
    sleepWhileAppIsUp(){
      while docker ps --filter=name=mongo | grep -qF mongo ; do
        sleep 2
      done
    }

    sleepWhileAppIsUp
  end script

  post-stop script
    if docker ps --filter=name=mongo | grep -qF mongo; then
      /opt/util/docker-compose/bin/docker-compose -f /opt/docker/mongo/docker-compose.yml stop
    fi
  end script

.. example code mongo-docker.conf

Expanding environment variables
-------------------------------

If you use environment variables in your YAML file they will be expanded
if the are of the form `${XYZ}`. The other form `$XYZ` is not expanded.
Expansion is only relevant for the parts that are copied (external port numbers,
name of container).

If you use this feature make sure that the environment variables are set in the
conf file. In ``systemd`` with::

  [Service]
  Environment=DOCKERIMAPPORT=143

and in Upstart::

  env DOCKERIMAPPORT=143

``dc2service`` will try to insert the right definitions for you.

Finding ``docker-compose``
--------------------------

As the full path to ``docker-compose`` will be inserted in the configuration
file, this path needs to be available. ``dc2service`` will search the PATH
environement variable for the locations. If your ``docker-compose`` is not in
your path you can hand the full path in with the option ``--docker-compose``
or specify this in the file
``~/.config/ruamel_dc2service/ruamel_dc2service.yaml``::

  global:
    docker-compose: /opt/util/docker-compose/bin/docker-compose



