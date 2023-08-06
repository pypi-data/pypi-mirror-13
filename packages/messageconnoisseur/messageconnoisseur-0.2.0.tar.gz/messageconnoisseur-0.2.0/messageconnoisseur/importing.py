''' Contains code for adding messages to the database '''
from __future__ import unicode_literals
import datetime
import logging
import os
import sqlite3
import re
from collections import namedtuple
from .common import Message


MessageFormat = namedtuple('MessageFormat',
                           ['id', 'regex', 'datestring', 'match_helper', 'fixyear'])
MESSAGE_FORMATS = [
    # Old export from Whatsapp on Android, does not contain year (only seen with messages from 2014)
    # Timestamp example: "1 May 18:22"
    MessageFormat(
        1, (r"^(?P<timestamp>\d{1,2} [A-Z][a-z]{2} \d{2}:\d{2}) - "
            r"(?P<author>[^:]*): (?P<content>.*?)(?=\n\d{1,2})"),
        "%d %b %H:%M", "\n00", 2014
        ),
    # More recent export from Whatsapp on Android, timestamp like "2015/03/23, 20:06"
    MessageFormat(
        2, (r"^(?P<timestamp>\d{4}\/\d{2}\/\d{2}, \d{2}:\d{2}) - "
            r"(?P<author>[^:]*): (?P<content>.*?)(?=\n\d{4})"),
        "%Y/%m/%d, %H:%M", "\n0000", 0
        ),
    # More recent export from Whatsapp on iOS, timestamp like "18/09/14 17:59:40"
    MessageFormat(
        3, (r"^(?P<timestamp>\d{2}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2}): "
            r"(?P<author>[^:]*): (?P<content>.*?)(?=\n\d{2})"),
        "%d/%m/%y %H:%M:%S", "\n00", 0
        ),
    # Older export from Whatsapp on iOS, timestamp like "06/01/14 04:19:11 pm"
    MessageFormat(
        4, (r"^(?P<timestamp>\d{2}\/\d{2}\/\d{2} \d{2}:\d{2}:\d{2} [ap]m): "
            r"(?P<author>[^:]*): (?P<content>.*?)(?=\n\d{2})"),
        "%d/%m/%y %I:%M:%S %p", "\n00", 0
        )
    ]

REGEX_FLAGS = re.DOTALL | re.MULTILINE

GARBAGE_CONTENT = [
    "<Media omitted>",
    "<image omitted>",
    "<video omitted>",
    "<audio omitted>",
    "<vCard omitted>",
]

def parse_string(self, data, formatspec):
    ''' Search a string for messages and parse them. '''
    to_parse = data.decode('utf-8') + formatspec.match_helper
    regex = re.compile(formatspec.regex, REGEX_FLAGS)
    matches = regex.findall(to_parse)
    results = []
    authors = set()
    trash_count = 0
    for match in matches:
        # Check whether match is useful
        is_garbage = False
        for item in GARBAGE_CONTENT:
            if item.upper() in match[2].upper():
                trash_count += 1
                is_garbage = True
                continue
        if is_garbage:
            continue

        # Determine author id
        try:
            author_id = self.author_map[match[1]]
        except KeyError:
            author_id = self.create_author(match[1])
            self.author_map[match[1]] = author_id
        authors.add(author_id)

        # Remove newlines from content
        content = match[2].replace('\n', '')

        # Parse timestring
        timestamp = datetime.datetime.strptime(
            match[0], formatspec.datestring
            ).replace(second=0)
        if formatspec.fixyear != 0:
            timestamp = timestamp.replace(year=formatspec.fixyear)

        # Store message in results
        results.append(Message(content, author_id, timestamp))
    logging.debug('Trashed %s messages', trash_count)
    return results, authors

def import_file(self, filename, formatspec):
    ''' Open file and import all messages. Format must be known. '''
    with open(filename, 'r') as fop:
        data = fop.read()

    results, _ = self.parse_string(data, formatspec)
    cursor = self.db_con.cursor()
    logging.info('Messages in file: %s', len(results))
    dupes = 0
    for message in results:
        try:
            cursor.execute(
                'INSERT INTO messages (content, author_id, timestamp) VALUES (?,?,?)',
                (message.content, message.author_id, message.timestamp))
        except sqlite3.IntegrityError:
            # Deduplication
            dupes += 1
            continue
    logging.info('Duplicates skipped: %s', dupes)
    self.db_con.commit()

def import_folder(self, folder):
    ''' Parse all files in a folder '''
    logging.info('Importing from folder %s', folder)
    for root, _, files in os.walk(folder):
        for fop in files:
            if fop.endswith('.txt'):
                logging.info('Importing file %s', fop)
                try:
                    formatspec = determine_format(fop)
                except ValueError:
                    logging.error('Could not determine format of file %s, skipping!', fop)
                    continue
                self.import_file(os.path.join(root, fop), formatspec)

def import_message(self, message):
    ''' Import a single message. Not suitable for batch use, commits every time. '''
    cursor = self.db_con.cursor()
    cursor.execute(
        'INSERT INTO messages (content, author_id, timestamp) VALUES (?,?,?)',
        (message.content, message.author_id, message.timestamp))
    self.db_con.commit()

def determine_format(filename):
    ''' Extract the format id from a file named like asdf.1.txt and return correct format '''
    f_id = int(re.match(r'.*\.(\d+)\.txt', filename).group(1))
    try:
        return MESSAGE_FORMATS[f_id - 1]
    except KeyError:
        if f_id:
            raise ValueError('Specified format does not exist!')
        else:
            raise ValueError('Could not extract format id from filename!')

def get_format_from_id(f_id):
    ''' Return the format with the specified id (not index) '''
    return MESSAGE_FORMATS[f_id - 1]
