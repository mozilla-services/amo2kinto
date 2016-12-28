import codecs
import json
import jsonschema
import requests
import six

from kinto_http import cli_utils, Client
from six.moves.urllib.parse import urljoin

from . import constants
from .amo import prepare_amo_records
from .kinto import get_kinto_records
from .logger import logger
from .synchronize import get_diff, push_changes


FIELDS = {
    'addons': ['blockID', 'os', 'guid', 'prefs', 'versionRange', 'details'],
    'certificates': ['serialNumber', 'issuerName', 'details'],
    'gfx': ['blockID', 'os', 'vendor', 'feature', 'featureStatus',
            'driverVersion', 'driverVersionmax', 'driverVersionComparator',
            'devices', 'versionRange', 'details'],
    'plugins': ['blockID', 'os', 'xpcomabi', 'infoURL', 'versionRange',
                'matchName', 'matchFilename', 'matchDescription', 'details']
}


def sync_records(amo_records, fields, kinto_client,
                 bucket, collection, config, permissions,
                 editor_client=None, reviewer_client=None,
                 ignore_incorrect_records=False):

    amo_records = prepare_amo_records(amo_records, fields)

    for record in amo_records:
        for versionRange in record['versionRange']:
            versionRange.setdefault('severity', 1)

    valid_records = amo_records
    if config:
        valid_records = []
        # We validate all amo_records to make sure nothing is broken
        # if we were to import everything.
        #
        # We could be validating only to_create records below but it
        # is a sane safety check.
        #
        for record in amo_records:
            try:
                jsonschema.validate(record, config['schema'])
            except jsonschema.exceptions.ValidationError as e:
                if ignore_incorrect_records:
                    logger.warn('Invalid record ignored: %s' % record['blockID'])
                    logger.info('Error was:\n %s' % e)
                    continue
                raise
            valid_records.append(record)


    kinto_records = get_kinto_records(
        kinto_client=kinto_client,
        bucket=bucket,
        collection=collection,
        config=config,
        permissions=permissions)

    to_create, to_update, to_delete = get_diff(valid_records, kinto_records)

    push_changes((to_create, to_update, to_delete), kinto_client,
                 bucket=bucket, collection=collection,
                 editor_client=editor_client, reviewer_client=reviewer_client)


def main(args=None):
    parser = cli_utils.add_parser_options(
        description='Import the blocklists from the addons server into Kinto.',
        default_collection=None,
        default_bucket=None,
        default_server=constants.KINTO_SERVER,
        default_auth=constants.AUTH,
        include_bucket=False,
        include_collection=False)

    parser.add_argument('-S', '--schema-file', help='JSON Schemas file',
                        type=str, default=constants.SCHEMA_FILE)

    parser.add_argument('--no-schema', help='Should we handle schemas',
                        action="store_true")

    parser.add_argument('--editor-auth',
                        help='Credentials to be used for requesting a review',
                        type=str, default=None)

    parser.add_argument('--reviewer-auth',
                        help='Credentials to be used for validating the review',
                        type=str, default=None)

    parser.add_argument('--certificates-bucket',
                        help='Bucket name for certificates',
                        type=str, default=constants.CERT_BUCKET)

    parser.add_argument('--certificates-collection',
                        help='Collection name for certificates',
                        type=str, default=constants.CERT_COLLECTION)

    parser.add_argument('--gfx-bucket', help='Bucket name for gfx',
                        type=str, default=constants.GFX_BUCKET)

    parser.add_argument('--gfx-collection',
                        help='Collection name for gfx',
                        type=str, default=constants.GFX_COLLECTION)

    parser.add_argument('--addons-bucket', help='Bucket name for addons',
                        type=str, default=constants.ADDONS_BUCKET)

    parser.add_argument('--addons-collection',
                        help='Collection name for addon',
                        type=str, default=constants.ADDONS_COLLECTION)

    parser.add_argument('--plugins-bucket', help='Bucket name for plugins',
                        type=str, default=constants.PLUGINS_BUCKET)

    parser.add_argument('--plugins-collection',
                        help='Collection name for plugin',
                        type=str, default=constants.PLUGINS_COLLECTION)

    parser.add_argument('-C', '--certificates',
                        help='Only import certificates',
                        action='store_true')

    parser.add_argument('-G', '--gfx', help='Only import GFX drivers',
                        action='store_true')

    parser.add_argument('-A', '--addons', help='Only import addons',
                        action='store_true')

    parser.add_argument('-P', '--plugins', help='Only import plugins',
                        action='store_true')

    # Addons Server selection
    parser.add_argument('--addons-server',
                        help='The addons server to import from',
                        type=str, default=constants.ADDONS_SERVER)

    parser.add_argument('--ignore-errors', help='Ignore validation errors',
                        action='store_true')

    args = parser.parse_args(args=args)
    cli_utils.setup_logger(logger, args)

    kinto_client = cli_utils.create_client_from_args(args)

    editor_client = None
    if args.editor_auth is not None:
        args.editor_auth = tuple(args.editor_auth.split(':', 1))
        editor_client = Client(server_url=args.server,
                               auth=args.editor_auth)

    reviewer_client = None
    if args.reviewer_auth is not None:
        args.reviewer_auth = tuple(args.reviewer_auth.split(':', 1))
        reviewer_client = Client(server_url=args.server,
                                 auth=args.reviewer_auth)

    # If none of the different "collections" were passed as parameter, then we
    # want to import them all.
    import_all = not any([
        args.certificates,
        args.gfx,
        args.addons,
        args.plugins])

    # Check if the schema capability is activated
    body, headers = kinto_client.session.request('get', '/')
    if 'schema' not in body.get('capabilities', {}):
        logger.warn('\t --- Server schema validation disabled --- \n')
        logger.warn("The server at {} won't validate the records against "
                    "the collection JSON schema. More information "
                    "http://kinto.readthedocs.io/en/stable/api/1.x/"
                    "collections.html?highlight=json%20validation"
                    "#collection-json-schema\n".format(args.server))

    # Load the schemas
    schemas = {}
    if not args.no_schema:
        with codecs.open(args.schema_file, 'r', encoding='utf-8') as f:
            schemas = json.load(f)['collections']

    blocklists_url = urljoin(args.addons_server, '/blocked/blocklists.json')
    resp = requests.get(blocklists_url)
    resp.raise_for_status()
    blocklists = resp.json()

    for collection_type, records in six.iteritems(blocklists):
        collection_type = collection_type.replace('-', '')
        if hasattr(args, collection_type) and (
                getattr(args, collection_type) or import_all):
            bucket = getattr(args, '%s_bucket' % collection_type)
            collection = getattr(args, '%s_collection' % collection_type)
            config = None
            if collection_type in schemas:
                config = schemas[collection_type]['config']
            sync_records(amo_records=records,
                         fields=FIELDS[collection_type],
                         kinto_client=kinto_client,
                         editor_client=editor_client,
                         reviewer_client=reviewer_client,
                         bucket=bucket,
                         collection=collection,
                         config=config,
                         permissions=constants.COLLECTION_PERMISSIONS,
                         ignore_incorrect_records=args.ignore_errors)

