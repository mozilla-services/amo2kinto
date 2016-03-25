import os

SCHEMA_FILE = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'schemas.json'))

# AMO defaults
AMO_SERVER = 'https://addons-dev.allizom.org/'

# Kinto server defaults
KINTO_SERVER = 'http://localhost:8888/v1'
AUTH = ('mark', 'p4ssw0rd')
COLLECTION_PERMISSIONS = {'read': ["system.Everyone"]}

# Buckets name default
ADDONS_BUCKET = u'staging'
ADDONS_COLLECTION = u'add-ons'
CERT_BUCKET = u'staging'
CERT_COLLECTION = u'certificates'
GFX_BUCKET = u'staging'
GFX_COLLECTION = u'gfx'
PLUGINS_BUCKET = u'staging'
PLUGINS_COLLECTION = u'plugins'
