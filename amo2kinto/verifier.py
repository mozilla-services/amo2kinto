"""Parse and normalize two XML files and then generate a diff of both."""
import argparse
import json
import logging
import os
import requests
import subprocess
import six
import sys
import tempfile
import xmltodict

logger = logging.getLogger('xml-verifier')

RECORD_SORT_FIELDS = (
    '@blockID', '@id', '@issuerName', 'serialNumber',
    '@guid', '@name', '@minVersion', '@maxVersion'
)


def get_unique_id(*fields):
    """Generated a unique sort id string for a given record."""
    def wraps(d):
        if isinstance(d, dict):
            return '-'.join([str(v) for v in (d.get(f) for f in fields)])
        else:
            return d

    return wraps


def sort_lists_in_dict(d):
    if not isinstance(d, dict):
        return d

    for key, value in six.iteritems(d):
        if isinstance(value, list):
            value = sorted(value, key=get_unique_id(*RECORD_SORT_FIELDS))
            value = [sort_lists_in_dict(v) for v in value]
        elif isinstance(value, dict):
            value = sort_lists_in_dict(value)
        elif isinstance(value, six.text_type):
            value = value.strip()

        d[key] = value
    return d


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Parse and normalize two XML files and '
        'generate a diff of both.')

    parser.add_argument('files', metavar='N',
                        help='Compare files, line by lines', nargs='+',)
    parser.add_argument('-k', '--keep-tmp-files', action="store_false",
                        dest='clean', help='Keep normalize temporary files')

    args = parser.parse_args(args=args)

    tmp_files = []

    for filepath in args.files:
        if not filepath.startswith('http') and not os.path.exists(filepath):
            logger.error("%s doesn't exists" % filepath)
            return 1

    last_updated = None

    for filepath in args.files:
        # Normalize XML
        curr_file = tempfile.NamedTemporaryFile("w", delete=False)
        tmp_files.append(curr_file)
        if filepath.startswith('http'):
            resp = requests.get(filepath)
            resp.raise_for_status()
            content = resp.text
        else:
            with open(filepath) as f:
                content = f.read()

        d = xmltodict.parse(content)
        # sort lists of the dict
        sort_lists_in_dict(d)

        # Ignore differences in the lastupdate blocklist tag
        # parameter. So that if they differs we ignore it.
        if not last_updated:
            last_updated = d['blocklist']['@lastupdate']
        else:
            d['blocklist']['@lastupdate'] = last_updated

        json.dump(d, curr_file, indent=4, sort_keys=True)
        curr_file.write('\n')

    # Close and clean files
    for f in tmp_files:
        f.close()

    diff_args = ['diff', '-U10', '-u'] + [tf.name for tf in tmp_files]

    # Print the diff command to stderr if we kept the file for debugging.
    if not args.clean:
        sys.stderr.write('$ %s\n' % ' '.join(diff_args))
    try:
        output = subprocess.check_output(diff_args, stderr=subprocess.STDOUT)
        sys.stdout.write(output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.output.decode('utf-8'))
        return 2

    if args.clean:
        for f in tmp_files:
            os.unlink(f.name)
    else:
        sys.stderr.write('$ %s\n' % ' '.join(diff_args))
