amo2kinto
#########

.. image:: https://img.shields.io/travis/mozilla-services/amo2kinto/master.svg
        :target: https://travis-ci.org/mozilla-services/amo2kinto

.. image:: https://img.shields.io/pypi/v/amo2kinto.svg
        :target: https://pypi.python.org/pypi/amo2kinto

.. image:: https://coveralls.io/repos/mozilla-services/amo2kinto/badge.svg?branch=master
        :target: https://coveralls.io/r/mozilla-services/amo2kinto

- **json2kinto**: Import ``addons-server`` blocklist into kinto
- **kinto2xml**: Export the blocklist in the legacy XML format
- **xml-verifier**: Show the differences between the ``addons-server`` XML file and the ``kinto2xml`` generated one.


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
- Building **cryptography** will require: ``build-essential libffi-dev libssl-dev python-dev``

Otherwise you will run into errors like:

- ``libxml/xmlversion.h: File not found``
- ``ffi.h: File not found``
- ``ssl.h: File not found``


Importing blocklists from the addons server into Kinto
======================================================

The `addons-server <https://github.com/mozilla/addons-server/>`_ is
able to export its blocklists database in JSON.

The script will create the bucket/collection with a given schema.

The last version of the schema file can be find here:
https://github.com/mozilla-services/amo-blocklist-ui/blob/master/amo-blocklist.json

You can use the ``make update-schemas`` command to fetch its last version.

You can use the ``json2kinto`` script to load this database into a
Kinto server::

    json2kinto --server http://localhost:8888/v1 \
               --addons-server https://addons.mozilla.org/  \
               --schema-file schemas.json


The script is able to synchronize (add new blocked items and remove old ones).

However if a blocked item already exists it won't be altered.

**json2kinto** gives you the ability to configure what you want to
load, with which user credentials and from which bucket and collection.

.. code-block::

    usage: json2kinto [-h] [--addons-server ADDONS_SERVER] [-s SERVER] [-a AUTH]
                      [-v] [-q] [-D] [-S SCHEMA_FILE] [--no-schema]
                      [--editor-auth EDITOR_AUTH]
                      [--reviewer-auth REVIEWER_AUTH]
                      [--certificates-bucket CERTIFICATES_BUCKET]
                      [--certificates-collection CERTIFICATES_COLLECTION]
                      [--gfx-bucket GFX_BUCKET] [--gfx-collection GFX_COLLECTION]
                      [--addons-bucket ADDONS_BUCKET]
                      [--addons-collection ADDONS_COLLECTION]
                      [--plugins-bucket PLUGINS_BUCKET]
                      [--plugins-collection PLUGINS_COLLECTION]
                      [-C] [-G] [-A] [-P]
                      [--ignore-errors]
    
    Import the blocklists from the addons server into Kinto.
    
    optional arguments:
      -h, --help            show this help message and exit
      --addons-server ADDONS_SERVER
                            The addons server to import from
      -s SERVER, --server SERVER
                            The location of the remote server (with prefix)
      -a AUTH, --auth AUTH  BasicAuth token:my-secret
      -v, --verbose         Show all messages.
      -q, --quiet           Show only critical errors.
      -D, --debug           Show all messages, including debug messages.
      -S SCHEMA_FILE, --schema-file SCHEMA_FILE
                            JSON Schemas file
      --no-schema           Should we handle schemas
      --editor-auth EDITOR_AUTH
                            Credentials to be used for requesting a review
      --reviewer-auth REVIEWER_AUTH
                            Credentials to be used for validating the review
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
      -C, --certificates    Only import certificates
      -G, --gfx             Only import GFX drivers
      -A, --addons          Only import addons
      -P, --plugins         Only import plugins
      --ignore-errors       Ignore validation errors


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


Show differences between two XML files
======================================

Once you've imported the data and exported them, you may want to
validate that both Kinto and addons server export the exact same data in XML.

You can use the ``xml-verifier`` command to validate that both files
are rendered the same way.

The **xml-verifier** command accept both files path and files URLs.


.. code-block::

    APPID="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"
    kinto2xml --app $APPID --app-version 46.0 -o generated-blocklists.xml
    xml-verifier https://blocklist.addons.mozilla.org/blocklist/3/$APPID/46.0/ generated-blocklists.xml


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
