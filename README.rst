#########
amo2kinto
#########


Installation
============

To install the release, just use::

    pip install amo2kinto


To install the development environment, just run::

    make install


System dependencies
-------------------

In order to build ``amo2kinto`` dependencies you may need the following libraries:

- Building **lxml** will require: ``libxml2-dev libxslt-dev python-dev``
- Building **cryptography** will require: ``build-essential libffi-dev libssl-dev python-dev``

If you have got error messages telling you a header file is missing, please install them:

- ``libxml/xmlversion.h: File not found``
- ``ffi.h: File not found``
- ``ssl.h: File not found``


Importing blocklists from AMO into Kinto
========================================

The `addons-server <https://github.com/mozilla/addons-server/>`_ is
able to export its blocklists database in JSON.

You can use the ``json2kinto`` script to load this database into a
kinto server::

    json2kinto --server http://localhost:8888/v1 \
               --amo-server https://addons.mozilla.org/  \
               --schema-file schemas.json

The last version of the schema file can be find here:
https://github.com/mozilla-services/amo-blocklist-ui/blob/master/amo-blocklist.json

The script is able to synchronize (add new blocked items and remove old ones).

However if a blocked item already exists it won't be altered.

**json2kinto** gives you the ability to configure what you want to
load, with which user credentials and in which bucket and collection.

.. code-block::

  -h, --help            show this help message and exit
  --amo-server AMO_SERVER
                        The AMO server to import from
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

If you want to export blocklists stored in Kinto in the AMO XML export
format, you can use the ``kinto2xml`` script::

    kinto2xml -s http://localhost:8888


**kinto2xml** gives you the ability to configure what you want to
export and in which bucket and collection are the data stored.

.. code-block::

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
validate that both Kinto and AMO export the exact same data in XML.

You can use the ``xml-verifier`` command to validate that both files
are rendered the same way::

    xml-verifier \
        https://blocklist.addons.mozilla.org/blocklist/3/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}/46.0/ \
        https://kinto-reader.dev.mozaws.net/v1/blocklist/3/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}/46.0/

The **xml-verifier** command accept both files path and files URLs::

   xml-verifier blocklists.xml generated-blocklists.xml
