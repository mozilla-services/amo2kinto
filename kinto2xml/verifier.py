"""Parse and normalize two XML files and then generate a diff of both."""
import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
import xmltodict

logger = logging.getLogger('xml-verifier')


def get_unique_id(*fields):
    def wraps(d):
        if isinstance(d, dict):
            return '-'.join([str(v) for v in (d.get(f) for f in fields)])
        else:
            return d

    return wraps


def sort_lists_in_dict(d):
    if not isinstance(d, dict):
        return d

    for key, value in d.iteritems():
        if isinstance(value, list):
            value = sorted(value, key=get_unique_id(
                '@blockID', '@id', '@issuerName', 'serialNumber',
                '@guid', '@name', '@minVersion', '@maxVersion'))
            value = [sort_lists_in_dict(v) for v in value]
        elif isinstance(value, dict):
            value = sort_lists_in_dict(value)

        d[key] = value
    return d


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Parse and normalize two XML files and '
        'generate a diff of both.')

    parser.add_argument('files', metavar='N',
                        help='Compare files, line by lines', nargs='+',)
    parser.add_argument('-b', '--ignore-space-change', action="store_true",
                        help='ignore changes in the amount of white space')
    parser.add_argument('-w', '--ignore-all-space', action="store_true",
                        help='ignore all white space')
    parser.add_argument('-k', '--keep-tmp-files', action="store_false",
                        dest='clean', help='Keep normalize temporary files')

    args = parser.parse_args(args=args)

    tmp_files = []

    for filepath in args.files:
        if not os.path.exists(filepath):
            logger.error("%s doesn't exists" % filepath)
            sys.exit(1)

    for filepath in args.files:
        # Normalize XML
        curr_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_files.append(curr_file)
        with open(filepath) as f:
            d = xmltodict.parse(f.read())
            # sort lists of the dict
            sort_lists_in_dict(d)
            json.dump(d, curr_file, indent=4, sort_keys=True)
            curr_file.write('\n')

    # Close and clean files
    for f in tmp_files:
        f.close()

    diff_args = ['diff', '-u']
    if args.ignore_space_change:
        diff_args.append('-b')

    if args.ignore_all_space:
        diff_args.append('-w')

    diff_args = diff_args + [tf.name for tf in tmp_files]

    # process diff
    sys.stderr.write('$ %s\n' % ' '.join(diff_args))
    try:
        sys.stdout.write(subprocess.check_output(diff_args,
                                                 stderr=subprocess.STDOUT))
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.output)

    if not args.clean:
        sys.stderr.write('$ %s\n' % ' '.join(diff_args))
    else:
        for f in tmp_files:
            os.unlink(f.name)
