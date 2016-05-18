CHANGELOG
#########

This document describes changes between each past release.

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
