amo2kinto
#########


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
                      [--certificates-bucket CERTIFICATES_BUCKET]
                      [--certificates-collection CERTIFICATES_COLLECTION]
                      [--gfx-bucket GFX_BUCKET] [--gfx-collection GFX_COLLECTION]
                      [--addons-bucket ADDONS_BUCKET]
                      [--addons-collection ADDONS_COLLECTION]
                      [--plugins-bucket PLUGINS_BUCKET]
                      [--plugins-collection PLUGINS_COLLECTION]
                      [-C] [-G] [-A] [-P]
    
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
                     [--plugins-collection PLUGINS_COLLECTION] [--app APP]
                     [-o OUT]
    
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
      --app APP             Targeted blocklists.xml APP id
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
    kinto2xml --app $APPID -o generated-blocklists.xml
    xml-verifier https://blocklist.addons.mozilla.org/blocklist/3/$APPID/46.0/ generated-blocklists.xml
