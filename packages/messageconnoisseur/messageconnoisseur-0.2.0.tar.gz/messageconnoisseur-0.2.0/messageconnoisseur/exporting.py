''' Contains code for exporting information about or from the database '''
from __future__ import unicode_literals
from .common import Message


def generate_leaderboard(self, limit=10):
    ''' Generate a list of author names and their message counts. '''
    cursor = self.db_con.cursor()
    cursor.execute(
        ('SELECT a.name, COUNT(*) FROM messages JOIN authors a ON author_id=a.id '
         'GROUP BY author_id ORDER BY COUNT(*) DESC LIMIT ?'),
        (limit, ))
    return cursor.fetchall()

def generate_time_leaderboard(self, year, month=None, limit=10):
    ''' Generate a leaderboard of a specified year or month. '''
    cursor = self.db_con.cursor()
    if month:
        date_spec = '{}-{:0>2}%'.format(year, month)
    else:
        date_spec = '{}%'.format(year)
    cursor.execute(
        ('SELECT a.name, COUNT(*) FROM messages JOIN authors a ON author_id=a.id '
         'WHERE timestamp LIKE ? GROUP BY author_id ORDER BY COUNT(*) DESC LIMIT ?'),
        (date_spec, limit))
    return cursor.fetchall()

def get_random_quote(self, include=None, exclude=None):
    ''' Get a random quote, return as message '''
    cursor = self.db_con.cursor()
    if not (include or exclude):
        query = ('SELECT content, author_id, timestamp FROM messages '
                 'WHERE author_id NOT IN ('
                 'SELECT id FROM authors WHERE noquote = 1)'
                 'ORDER BY RANDOM(*) LIMIT 1')
        cursor.execute(query)
    else:
        thelist = include or exclude
        placeholder = ['?'] * len(thelist)
        placeholders = ','.join(placeholder)
        invert = 'NOT' if exclude else ''
        query = ('SELECT content, author_id, timestamp FROM messages '
                 'WHERE author_id {} IN ({}) '
                 'AND author_id NOT IN ('
                 'SELECT id FROM authors WHERE noquote = 1)'
                 'ORDER BY RANDOM(*) LIMIT 1').format(invert, placeholders)
        cursor.execute(query, thelist)

    result = cursor.fetchone()
    if result:
        return Message(result[0], result[1], result[2])
    else:
        return None
