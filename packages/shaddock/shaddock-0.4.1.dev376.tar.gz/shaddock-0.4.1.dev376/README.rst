**Shaddock**
============
Shaddock provides a platform deployed in http://docker.com containers following
a predefined template (like an http://openstack.org infrastructure)

QuickStart
----------

.. code:: bash

    # Installation:
    git clone https://github.com/epheo/shaddock
    cd shaddock
    sudo python setup.py install

    # Configuration:
    cd examples && ./set_ip.sh openstack.yml

    # Usage:
    shaddock -f examples/openstack.yml
    (shaddock) ps
    (shaddock) pull all
    (shaddock) start all

**Run the shaddock shell in a container:**

Without installation but require the docker API to listen on a tcp port.

.. code:: bash

    docker run --rm -i -v examples:/examples --env DOCKER_HOST="https://<docker_api>:2376" --env TEMPLATE_FILE=/examples/openstack.yml -t shaddock/shaddock



OpenStack template configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can find a reference template for an OpenStack platform in the examples/ directory.
This template point to OpenStack services Docker images hosted in the public Docker repository.

You can/should of course create your own template file following the same architecture using the needed Docker images.

In case you would *build* and use your own images you can specify a directory of Dockerfiles to Shaddock with the '-d' option.

The directory should follow this hierarchy: directory/user/image/Dockerfile
You will find the one used in order to build the demonstration OpenStack images at https://github.com/epheo/shaddock-openstack


Structure example of a template file:

.. code:: yaml

    - name: glance
      image: shaddock/glance:latest
      priority: 50
      ports:
        - 9292
        - 4324
      volumes:
        - mount: /var/log/glance
          host_dir: /var/log/shaddock/glance
      depends-on:
        - {name: mysql, port: 3306}
        - {name: keystone, port: 5000, get: '/v2.0'}
        - {name: keystone, port: 35357, get: '/v2.0'}
      env:
        MYSQL_HOST_IP: <your_ip>
        KEYSTONE_HOST_IP: <your_ip>
        GLANCE_DBPASS: panama
        GLANCE_PASS: panama

Tests:

.. code:: yaml

     - {name: nova, status: stopped}
     - {name: nova, port: 8774, type: tcp}
     - {name: nova, port: 8774, state: down, type: tcp}
     - {host: google.com, port: 8774, state: down, type: tcp}
     - {name: nova, type: http, get: '/v2.0', port: 5000, code: 200}
     - {host: google.com, type: http, get: '/v2.0', port: 5000, code: 200}
     - {host: 127.0.0.1, type: http, get: '/', code: 200, useproxy: False }
     - {name: nova, sleep: 20} # defaults to 10
     - {name: nova, retry: 10} # defaults to 5

Usage
-----

.. code:: bash

    shaddock --help


.. code:: raw

    usage: shaddock [--version] [-v] [--log-file LOG_FILE] [-q] [-h] [--debug]
                    [-H DOCKER_HOST] [--tlscert DOCKER_CERT_PATH]
                    [--tlskey DOCKER_KEY_PATH] [--tlscacert DOCKER_CACERT_PATH]
                    [--tlsverify DOCKER_TLS_VERIFY] [--tls DOCKER_TLS]
                    [--docker-version DOCKER_VERSION] [-f TEMPLATE_FILE]
                    [-d IMAGES_DIR]


.. code:: raw

    optional arguments:
      --version             Show program's version number and exit.
      -v, --verbose         Increase verbosity of output. Can be repeated.
      --log-file LOG_FILE   Specify a file to log output. Disabled by default.
      -q, --quiet           Suppress output except warnings and errors.
      -h, --help            Show this help message and exit.
      --debug               Show tracebacks on errors.
      -H DOCKER_HOST, --host DOCKER_HOST
                            IP/hostname to the Docker API. (Env: DOCKER_HOST)
      --tlscert DOCKER_CERT_PATH
                            Path to TLS certificate file. (Env: DOCKER_CERT_PATH)
      --tlskey DOCKER_KEY_PATH
                            Path to TLS key file. (Env: DOCKER_KEY_PATH)
      --tlscacert DOCKER_CACERT_PATH
                            Trust only remotes providing a certificate signed by
                            the CA given here. (Env: DOCKER_CACERT_PATH)
      --tlsverify DOCKER_TLS_VERIFY
                            Use TLS and verify the remote. (Env:
                            DOCKER_TLS_VERIFY)
      --tls DOCKER_TLS      Use TLS; implied by tls-verify flags. (Env:
                            DOCKER_TLS)
      --docker-version DOCKER_VERSION
                            Docker API version number (Env: DOCKER_VERSION)
      -f TEMPLATE_FILE, --template-file TEMPLATE_FILE
                            Template file to use. (Env: TEMPLATE_FILE)
      -d IMAGES_DIR, --images-dir IMAGES_DIR
                            Directory to build Docker images from.(Env:
                            IMAGES_DIR)


.. code:: raw

    Commands:
      build          Build a new container
      create         Create a new container
      help           print detailed help for another command
      info           Show details about a container
      list           Show a list of Containers.
      logs           Display the logs of a container
      ps             Show a list of Containers.
      pull           Pull a container from the Docker Repository
      remove         Remove a container
      restart        Restart a container
      show           Show details about a container
      start          Start a new container
      stop           Stop a container


Informations
------------

License
~~~~~~~
Shaddock is licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License. You may obtain a
copy of the License at http://www.apache.org/licenses/LICENSE-2.0

References
~~~~~~~~~~

Docker-py API Documentation: http://docker-py.readthedocs.org/

OpenStack Official Documentation: http://docs.openstack.org/

Help
~~~~

**Set up the Docker remote API:**

refs: https://docs.docker.com/reference/api/docker_remote_api/


.. code:: bash

    cat /etc/default/docker.io
    DOCKER_OPTS="-H tcp://0.0.0.0:2376 -H unix:///var/run/docker.sock"


**Docker installation:**

refs: https://docs.docker.com/installation/
