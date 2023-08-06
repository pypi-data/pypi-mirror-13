''' Contains script entry points to manipulate databases from the shell '''
from __future__ import unicode_literals
import argparse
import logging
import os
import sys
from . import Connoisseur
from .importing import determine_format, get_format_from_id


logging.basicConfig(level=logging.INFO)

def import_directory_script():
    ''' Import a directory of logs into a database. Database is created if not exists. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('database', help='the database to write to (created if not exists)')
    parser.add_argument('directory', help='the directory of files to parse')

    args = parser.parse_args()
    conn = Connoisseur(args.database)

    if not os.path.isdir(args.directory):
        logging.critical('The directory %s does not exist!', args.directory)
        sys.exit(1)

    conn.import_folder(args.directory)
    sys.exit(0)

def import_file_script():
    ''' Import a single file into a database. Database is created if not exists. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', type=int, help='manually specify format id')
    parser.add_argument('database', help='the database to write to (created if not exists)')
    parser.add_argument('file', help='the file to parse')

    args = parser.parse_args()
    conn = Connoisseur(args.database)

    if not os.path.isfile(args.file):
        logging.critical('The file %s does not exist!', args.file)
        sys.exit(1)

    if args.format:
        try:
            formatspec = get_format_from_id(args.format)
        except KeyError:
            logging.critical('The specified format does not exist!')
            sys.exit(1)
    else:
        try:
            formatspec = determine_format(args.file)
        except ValueError:
            logging.critical('Could not determine message format of file %s! '
                             'Specify manually using --format or rename file.', args.file)
            sys.exit(1)

    conn.import_file(args.file, formatspec)
    sys.exit(0)
