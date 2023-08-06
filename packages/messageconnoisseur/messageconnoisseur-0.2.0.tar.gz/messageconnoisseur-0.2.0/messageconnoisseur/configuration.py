''' Contains configuration code '''
from __future__ import unicode_literals
import sqlite3
import logging


# Authors
def list_authors(self):
    ''' Create a list of all authors known in the database '''
    cursor = self.db_con.cursor()
    cursor.execute('SELECT id,name FROM authors')
    return cursor.fetchall()

def create_author(self, name):
    ''' Add a new author to the database, return id '''
    cursor = self.db_con.cursor()
    try:
        cursor.execute('SELECT author_id FROM nicknames WHERE nickname = ?',
                       (name,))
        nick = cursor.fetchone()
        if nick:
            return nick[0]
        cursor.execute('INSERT INTO authors (name) VALUES (?)',
                       (name,))
        self.db_con.commit()
        logging.info('Author %s created: %s', cursor.lastrowid, repr(name))
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Authorname already exists, return that id instead:
        cursor.execute('SELECT id FROM authors WHERE name = ?',
                       (name,))
        result = cursor.fetchone()
        return result[0]

# Nicknames
def list_nicknames(self):
    ''' Create a list of all nicknames in the database '''
    cursor = self.db_con.cursor()
    cursor.execute('SELECT author_id,nickname FROM nicknames')
    return cursor.fetchall()

def create_nickname(self, nickname, author_id):
    ''' Add a nickname to the database '''
    cursor = self.db_con.cursor()
    try:
        cursor.execute('INSERT INTO nicknames (nickname, author_id) VALUES (?,?)',
                       (nickname, author_id))
        self.db_con.commit()
        self.author_map = self.build_author_dict()
        logging.info('Nickname %s created.', repr(nickname))
    except sqlite3.IntegrityError:
        logging.debug('Tried to create existing nick %s', nickname)

def create_nickname_and_author(self, nickname, author_name):
    ''' Create nickname by author name, creates author if not exists '''
    author_id = self.create_author(author_name)
    self.create_nickname(nickname, author_id)

def name_to_id(self, name):
    ''' Looks up the id corresponding with the author name or nickname, if any '''
    cursor = self.db_con.cursor()

    queries = [
        'SELECT id FROM authors WHERE name LIKE ?',
        'SELECT id FROM nicknames WHERE nickname LIKE ?'
        ]

    for query in queries:
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]

    return None

def id_to_name(self, author_id):
    ''' Looks up the name of the author with the given id, or raises KeyError. '''
    cursor = self.db_con.cursor()

    query = 'SELECT name FROM authors WHERE id = ?'
    cursor.execute(query, (author_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        raise IndexError('Unknown ID!')

def build_author_dict(self):
    ''' Create a dict that can link an author name to an id '''
    result = {}

    authors = self.list_authors()
    for author in authors:
        result[author[1]] = author[0]
    nicks = self.list_nicknames()
    for nick in nicks:
        result[nick[1]] = nick[0]

    return result
