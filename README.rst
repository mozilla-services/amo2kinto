kinto2xml
---------

Generate a blocklist.xml file from Kinto collections.

.. code-block::

    usage: kinto2xml [-h] [-s SERVER] [-a AUTH] [-b BUCKET] [-v] [-q] [-D]
                     [-o OUT]

    Build a blocklists.xml file.

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
      -o OUT, --out OUT     Output file.
