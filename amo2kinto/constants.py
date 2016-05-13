import os

SCHEMA_FILE = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'schemas.json'))

# Addons Server defaults
ADDONS_SERVER = 'https://addons-dev.allizom.org/'

# Kinto server defaults
KINTO_SERVER = 'http://localhost:8888/v1'
AUTH = ('mark', 'p4ssw0rd')
COLLECTION_PERMISSIONS = {}

# Buckets name default
ADDONS_BUCKET = u'staging'
ADDONS_COLLECTION = u'addons'
CERT_BUCKET = u'staging'
CERT_COLLECTION = u'certificates'
GFX_BUCKET = u'staging'
GFX_COLLECTION = u'gfx'
PLUGINS_BUCKET = u'staging'
PLUGINS_COLLECTION = u'plugins'


# APP ID
FIREFOX_APPID = '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}'
THUNDERBIRD_APPID = '{3550f703-e582-4d05-9a08-453d09bdfdc6}'
SEAMONKEY_APPID = '{92650c4d-4b8e-4d2a-b7eb-24ecf4f6b63a}'
ANDROID_APPID = '{aa3c5121-dab2-40e2-81ca-7ea25febc110}'
