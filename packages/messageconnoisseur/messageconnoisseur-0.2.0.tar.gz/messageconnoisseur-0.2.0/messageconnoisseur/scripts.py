''' Contains script entry points to manipulate databases from the shell '''
from __future__ import unicode_literals
from __future__ import print_function
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

def leaderboard_all_time_script():
    ''' Generate a message count overview of all messages. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('database', help='the database to read from')
    parser.add_argument('--year', '-y', type=int, default=None)
    parser.add_argument('--month', '-m', type=int, default=None)
    parser.add_argument('--ugly', '-u', help='don\'t pretty-print output',
                        action='store_true')
    parser.add_argument('--limit', '-n', '-l', help='maximum number of entries',
                        default=10)

    args = parser.parse_args()
    if not os.path.isfile(args.database):
        logging.critical('The database %s could not be found!', args.database)
        sys.exit(1)

    conn = Connoisseur(args.database)
    if not args.year:
        result = conn.generate_leaderboard(limit=args.limit)
    elif not args.month:
        result = conn.generate_time_leaderboard(args.year, limit=args.limit)
    else:
        result = conn.generate_time_leaderboard(args.year, args.month, limit=args.limit)
    if args.ugly:
        print(result)
        sys.exit(0)
    else:
        print(prettyprint_leaderboard(result))

def random_quote_script():
    ''' Get a (semi-)random quote from the database. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('database', help='the database to read from')
    parser.add_argument('--format', '-f', help='what to show', default='content',
                        choices=['content', 'author', 'full'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--include', '-i', help='only select from specified authors',
                       action='append')
    group.add_argument('--exclude', '-e', help='don\'t select from specified authors',
                       action='append')

    args = parser.parse_args()
    if not os.path.isfile(args.database):
        logging.critical('The database %s could not be found!', args.database)
        sys.exit(1)

    conn = Connoisseur(args.database)

    # map any names passed in include or exclude to ids or error out
    thelist = args.include or args.exclude  # mutually exclusive
    if thelist:
        for i in xrange(len(thelist)):
            try:
                int(thelist[i])
            except ValueError:
                author_id = conn.name_to_id(thelist[i])
                if not author_id:
                    logging.error('Could not map name %s to id, exiting.',
                                  thelist[i])
                    sys.exit(1)
                thelist[i] = author_id

    result = conn.get_random_quote(args.include, args.exclude)
    if result:
        print(result.content)
        if args.format == 'author':
            print('  -- {}'.format(conn.id_to_name(result.author_id)))
        elif args.format == 'full':
            print('  -- {}, {}'.format(
                conn.id_to_name(result.author_id), result.timestamp))
    else:
        print('No quote could be retrieved.')

def prettyprint_leaderboard(board):
    ''' Prettyprints a leaderboard and returns string '''
    result = ''
    longest_name = max(
        [item[0] for item in board], key=lambda x: len(str(x)))
    max_namelen = len(longest_name)
    longest_number = max(
        [item[1] for item in board], key=lambda x: len(str(x)))
    max_scorelen = len(str(longest_number))
    format_string = '{:<' + str(max_namelen) + '} {:>' + str(max_scorelen) + '}'
    for item in board:
        result = result + format_string.format(item[0], item[1])
        if item != board[-1]:
            result = result + '\n'
    return result
