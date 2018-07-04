CHANGELOG
#########

This document describes changes between each past release.

4.0.0 (2018-07-04)
==================

**Bug fix**

- Fix the affected users section (#87), thanks @rctgamer3!

**Breaking changes**

- Removed code in charge of updating the collection schema (#85)


3.2.1 (2018-02-28)
==================

- Fix bug with Python 3 and writing files (#80).


3.2.0 (2018-02-06)
==================

- Filter add-ons and plugins in v3 based on the requesting application and version. (#74)
- Stop exporting cert items to Firefox 58 and above, where they aren't used. (#75)


3.1.0 (2017-10-03)
==================

- Add support for cert items subject and pubKeyHash attributes. (#70)


3.0.0 (2017-09-14)
==================

- Remove json2kinto importer
- Remove xml verifier


2.0.1 (2017-06-02)
==================

**Bug fix**

- Fix synchronize kinto-http parameters. (#67)


2.0.0 (2017-06-02)
==================

**Breaking changes**

- Upgrade to kinto-http.py 8.0 and drop support for Python < 3.5


1.7.2 (2017-02-20)
==================

- Fix XML exporter on missing blockID. (#63)


1.7.1 (2016-11-24)
==================

**Bug fix**

- Allow the importer to work even without the permission to create collections. (#56)
- Use ``PUT`` instead of ``PATCH`` to fully overwrite the destination with the source (#58)


1.7.0 (2016-11-21)
==================

**New features**

- Retry downloading the XML in case it fails the first time. (#50)


**Bug fix**

- Remove redundant footer when generating pages. (#51)
- Allow the importer to work even without the permission to create buckets. (#53)

**Internal changes**

- Improve the way the Makefile works (#52)


1.6.0 (2016-10-04)
==================

**New features**

- Add a configurable signoff workflow to-review → to-sign (#48)


1.5.1 (2016-09-08)
==================

**Bug fix**

- session_kwargs is not accessible anymore with last kinto-http client release. (#45)


1.5.0 (2016-08-25)
==================

- Add the ``blockpages-generator`` CLI tool (#43)


1.4.1 (2016-08-02)
==================

- Fix blockID ordering to make it the same as the addons-server.


1.4.0 (2016-07-18)
==================

**New features**

- Add version ranges for GFX items (#39) â `Bug 1283601`_

.. _`Bug 1283601`: https://bugzilla.mozilla.org/show_bug.cgi?id=1283601


1.3.1 (2016-07-06)
==================

**Bug fix**

- Fix patch_records properties.


1.3.0 (2016-07-06)
==================

- Update records that were changed (#37)


1.2.1 (2016-05-26)
==================

**Bug fix**

- kinto_client.delete_records API changed. (#35)


1.2.0 (2016-05-26)
==================

**New features**

- Let people specify ``--app-version`` and ``--api-version`` while using kinto2xml (#33)
- Add functional tests for both version of the XML file format. (#33)
- Configure the kinto-admin as well as the JSONSchema (#32)

**Bug fix**

- Group addons by the biggest guid (#33)


1.1.0 (2016-05-18)
==================

**Bug fix**

- In case there is a diff using xml-verifier, the command now returns an error code (#28)

**Internal changes**

- ``json2kinto`` does not set destination collections as publicly readable (#27)


1.0.0 (2016-05-12)
==================

**Breaking changes**

- kinto2xml was renamed amo2kinto (#21)
- New JSON Schema file format with a "collection" prefix (#22)

**New features**

- Use the schema to validate AMO records in the importer script. (#5)
- Warn if the server does not have the schema capability (#24)

**Internal changes**

- Document amo2kinto commands: json2kinto, kinto2xml and verifier. (#23)


0.1.0 (2016-04-27)
==================

**Initial version**

- Create collection with the definition of the JSON schema.
- Fetch AMO blocklists information from the /blocked/blocklists.json AMO endpoint.
- Handle import configuration on the CLI.
  - Bucket / Collection names
  - Remote AMO endpoint configuration
  - Schema file path configuration
  - Schema or not schema
  - Verbosity level
  - Server selection
  - Auth credentials
  - Importation type selection
- Support for kinto-signer triggering
- Full SSL support for Python 2.7
- Full Python 2.7 and Python 3.4/3.5 support
- Handle the enabled flag to activate records
- Makefile rule to update the schema definition
- Export kinto blocklists in XML blocklist file version 2
- Export kinto blocklists in XML blocklist file version 3
- XML verifier that create a diff of two XML files
