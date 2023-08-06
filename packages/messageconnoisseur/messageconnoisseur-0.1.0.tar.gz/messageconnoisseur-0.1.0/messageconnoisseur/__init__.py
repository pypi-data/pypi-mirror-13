''' MessageConnoisseur: collector of messages. '''
from __future__ import unicode_literals
import sqlite3


class Connoisseur(object):
    ''' Provides methods to store messages in a database. '''
    # pylint: disable=too-few-public-methods
    from .configuration import list_nicknames, list_authors, build_author_dict
    from .configuration import create_author, create_nickname_and_author, create_nickname
    from .importing import parse_string, import_file, import_folder

    def __init__(self, database_name):
        self.db_con = sqlite3.connect(database_name)
        self.db_con.executescript('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
                );

            CREATE TABLE IF NOT EXISTS nicknames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT UNIQUE,
                author_id INTEGER,
                FOREIGN KEY(author_id) REFERENCES authors(id)
                );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                timestamp TIMESTAMP,
                author_id INTEGER,
                FOREIGN KEY(author_id) REFERENCES authors(id),
                UNIQUE(content, timestamp, author_id)
                );
            ''')
        self.author_map = self.build_author_dict()
