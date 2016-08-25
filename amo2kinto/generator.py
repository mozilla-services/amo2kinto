import os
import datetime

from dateutil.parser import parse as dateutil_parser
from jinja2 import Environment, PackageLoader
from kinto_http import cli_utils

from . import constants
from .logger import logger


JSON_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
COLLECTION_FORMAT = '/buckets/{bucket_id}/collections/{collection_id}'


def iso2human(value):
    date = dateutil_parser(value)
    return date.strftime('%b %d, %Y')


def get_template(name):
    loader = PackageLoader('amo2kinto', 'templates')
    env = Environment(loader=loader)
    env.filters['datetime'] = iso2human
    return env.get_template(name)


def generate_index(records, template, target_dir):

    def sort_records(record):
        return record['details']['created'], record['last_modified']

    records = sorted(records, key=sort_records, reverse=True)
    res = template.render(records=records)
    filename = os.path.join(target_dir, 'index.html')

    logger.info('Writing %s' % filename)
    with open(filename, 'w') as f:
        f.write(res.encode('utf8'))


def generate_record(record, template, target_dir, get_filename):
    res = template.render(record=record)
    filename = os.path.join(target_dir, get_filename(record))

    logger.info('Writing %s' % filename)

    # This needs to be able to write to S3
    with open(filename, 'w') as f:
        f.write(res.encode('utf-8'))


def get_record_filename(record):
    return '%s.html' % record.get('blockID', record['id'])


def generate(client, collections, target_dir, collection_template, record_template):
    logger.info('Reading data from Kinto %s...' % client.session.server_url)
    records = []

    for collection_uri in collections:
        parts = collection_uri.strip('/').split('/')
        bucket_id = parts[1]
        collection_id = parts[3]

        logger.warn('Reading records from %s...' % collection_uri)
        response = client.get_records(bucket=bucket_id, collection=collection_id)
        for record in response:
            record.setdefault('details', {})
            if 'created' not in record['details']:
                date = datetime.date.fromtimestamp(record['last_modified'] / 1000)
                record['details']['created'] = date.strftime(JSON_DATE_FORMAT)
            records.append(record)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    col_tpl = get_template(collection_template)
    rec_tpl = get_template(record_template)

    logger.warn('Generating index...')
    generate_index(records, col_tpl, target_dir)

    logger.warn('Generating records files...')
    for record in records:
        generate_record(record, rec_tpl, target_dir, get_record_filename)


def main(args=None):
    parser = cli_utils.add_parser_options(
        description='Generate blocked item description files.',
        default_collection=None,
        default_bucket=constants.DESTINATION_BUCKET,
        default_server=constants.KINTO_SERVER,
        default_auth=constants.AUTH,
        include_collection=False)

    parser.add_argument('--addons-collection',
                        help='Collection name for addon',
                        type=str, default=constants.ADDONS_COLLECTION)

    parser.add_argument('--plugins-collection',
                        help='Collection name for plugin',
                        type=str, default=constants.PLUGINS_COLLECTION)

    parser.add_argument('-d', '--target-dir',
                        help='Destination directory to write files in.',
                        type=str, default=constants.TARGET_DIR)

    args = parser.parse_args(args=args)
    cli_utils.setup_logger(logger, args)

    kinto_client = cli_utils.create_client_from_args(args)

    collections = [
        COLLECTION_FORMAT.format(bucket_id=args.bucket,
                                 collection_id=args.addons_collection),
        COLLECTION_FORMAT.format(bucket_id=args.bucket,
                                 collection_id=args.plugins_collection),
    ]
    generate(kinto_client, collections, args.target_dir, 'collection.tpl', 'record.tpl')
