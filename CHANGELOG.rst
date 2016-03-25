CHANGELOG
#########

This document describes changes between each past release.

0.1.0 (unreleased)
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
