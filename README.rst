amo2kinto
#########

.. image:: https://img.shields.io/travis/mozilla-services/amo2kinto/master.svg
        :target: https://travis-ci.org/mozilla-services/amo2kinto

.. image:: https://img.shields.io/pypi/v/amo2kinto.svg
        :target: https://pypi.python.org/pypi/amo2kinto

.. image:: https://coveralls.io/repos/mozilla-services/amo2kinto/badge.svg?branch=master
        :target: https://coveralls.io/r/mozilla-services/amo2kinto

- **kinto2xml**: Export the blocklist in the legacy XML format
- **blockpages-generator**: Generate the blocklist documentation pages.


Installation
============

To install the release::

    pip install amo2kinto


To install the development environment::

    make install


System dependencies
-------------------

In order to build ``amo2kinto`` dependencies you may need the following libraries:

- Building **lxml** will require: ``libxml2-dev libxslt-dev python-dev``

Otherwise you will run into errors like:

- ``libxml/xmlversion.h: File not found``


Generate a blocklist.xml file from Kinto collections
====================================================

If you want to export blocklists stored in Kinto in the addons server XML export
format, you can use the ``kinto2xml`` script::

    kinto2xml -s http://localhost:8888/v1


**kinto2xml** gives you the ability to configure what you want to
export and in which bucket and collection are the data stored.

.. code-block::

    usage: kinto2xml [-h] [-s SERVER] [-a AUTH] [-v] [-q] [-D]
                     [--certificates-bucket CERTIFICATES_BUCKET]
                     [--certificates-collection CERTIFICATES_COLLECTION]
                     [--gfx-bucket GFX_BUCKET] [--gfx-collection GFX_COLLECTION]
                     [--addons-bucket ADDONS_BUCKET]
                     [--addons-collection ADDONS_COLLECTION]
                     [--plugins-bucket PLUGINS_BUCKET]
                     [--plugins-collection PLUGINS_COLLECTION]
                     [--api-version API_VERSION] [--app APP]
                     [--app-version APP_VERSION] [-o OUT]
    
    Build a blocklists.xml file from Kinto blocklists.
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SERVER, --server SERVER
                            The location of the remote server (with prefix)
      -a AUTH, --auth AUTH  BasicAuth token:my-secret
      -v, --verbose         Show all messages.
      -q, --quiet           Show only critical errors.
      -D, --debug           Show all messages, including debug messages.
      --certificates-bucket CERTIFICATES_BUCKET
                            Bucket name for certificates
      --certificates-collection CERTIFICATES_COLLECTION
                            Collection name for certificates
      --gfx-bucket GFX_BUCKET
                            Bucket name for gfx
      --gfx-collection GFX_COLLECTION
                            Collection name for gfx
      --addons-bucket ADDONS_BUCKET
                            Bucket name for addons
      --addons-collection ADDONS_COLLECTION
                            Collection name for addon
      --plugins-bucket PLUGINS_BUCKET
                            Bucket name for plugins
      --plugins-collection PLUGINS_COLLECTION
                            Collection name for plugin
      --api-version API_VERSION
                            Targeted blocklists.xml APP id
      --app APP             Targeted blocklists.xml APP id
      --app-version APP_VERSION
                            The targetted app version
      -o OUT, --out OUT     Output XML file.


Generate blocked addons and plugins description pages
=====================================================

You might want to export the human readable list and description of
add-ons and plugins that were blocked.

You can do that using the ``blockpages-generator`` cli tool:

.. code-block::

    usage: blockpages-generator [-h] [-s SERVER] [-a AUTH] [-b BUCKET] [-v] [-q]
                                [-D] [--addons-collection ADDONS_COLLECTION]
                                [--plugins-collection PLUGINS_COLLECTION]
                                [-d TARGET_DIR]
    
    Generate blocked item description files.
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SERVER, --server SERVER
                            The location of the remote server (with prefix)
      -a AUTH, --auth AUTH  BasicAuth token:my-secret
      -b BUCKET, --bucket BUCKET
                            Bucket name.
      -v, --verbose         Show all messages.
      -q, --quiet           Show only critical errors.
      -D, --debug           Show all messages, including debug messages.
      --addons-collection ADDONS_COLLECTION
                            Collection name for addon
      --plugins-collection PLUGINS_COLLECTION
                            Collection name for plugin
      -d TARGET_DIR, --target-dir TARGET_DIR
                            Destination directory to write files in.

It will generate an ``index.html`` file with the list of records
present in the ``addons`` and ``plugins`` collections in the
``target-dir`` directory.

It will also generate a file per ``add-on`` and ``plugin`` using the
``blockID`` or the ``id``. e.g ``i487.html`` or
``08db5018-2c80-4c4d-aa98-dafe6aacc28c.html``
