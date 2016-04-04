"""Parse and normalize two XML files and then generate a diff of both."""
import argparse
import logging
import os
import subprocess
import sys
import tempfile
from xml.dom import minidom

logger = logging.getLogger('xml-verifier')


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
        curr_file = tempfile.NamedTemporaryFile(delete=args.clean)
        tmp_files.append(curr_file)
        with open(filepath) as f:
            dom = minidom.parse(f)
            dom.writexml(curr_file)

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

    # Close and clean files
    for f in tmp_files:
        f.close()

    if not args.clean:
        sys.stderr.write('$ %s\n' % ' '.join(diff_args))
