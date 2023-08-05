.. _a Docker-based mini-PaaS: http://shortcircuit.net.au/~prologic/blog/article/2015/03/24/a-docker-based-mini-paas/


autodock-hipache
================

.. image:: https://badge.imagelayers.io/prologic/autodock-hipache:latest.svg
   :target: https://imagelayers.io/?images=prologic/autodock-hipache:latest
   :alt: Image Layers

Hipache Plugin for autodock.

autodock-hipache is MIT licensed.

.. note:: See: `autodock <https://github.com/prologic/autodock>`_

Basic Usage
-----------

Start the daemon::
    
    $ docker run -d --name autodock prologic/autodock

Link and start the autodock Hipache Plugin::
    
    $ docker run -d --link autodock prologic/autodock-hipache

Now whenever you start a new container autodock will listen for Docker events
and discover containers that have been started. The ``autodock-hipache`` plugin
will specifically listen for starting containers that have a ``VIRTUALHOST``
environment variable and reconfigure the running ``hipache`` container.

An optional ``ALIAS`` environment value can be given as an extra virtualhost
typically used for a ``www.`` alias to a domain.

Start a "Hello World" Web Application::
    
    $ docker run -d -e VIRTUALHOST=hello.local prologic/hello
    curl -q -o - -H 'Host: hello.local' http://localhost/
    Hello World!

.. note:: This method of hosting and managing webapps and websites is in
          production deployments and talked about in more detail in the post
          `A Docker-based mini-PaaS`.

``docker-compose.yml``:

.. code:: yaml
    
   autodock:
       image: prologic/autodock
       volumes:
           - /var/run/docker.sock:/var/run/docker.sock

   autodockhipache:
       image: prologic/autodock-hipache
       links:
           - autodock
           - hipache:redis

   sslcerts:
       image: prologic/mksslcrt
       command: "*.mydomain.com"

   hipache:
       image: prologic/hipache
       ports:
           - "80:80"
           - "443:443"
       volumes_from:
           - sslcerts

   hello:
       image: prologic/hello
       environment:
           - VIRTUALHOST=hello.mydomain.com
           - ALIAS=hello.local

.. note:: The version of Hipache used here will not startup unless you have
          setup SSL certificates, so the sslcerts volume is requried for
          a correctly functionining system.
