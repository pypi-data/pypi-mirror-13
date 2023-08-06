''' Contains classes used in more than one place '''
from __future__ import unicode_literals
from collections import namedtuple


Message = namedtuple('Message', ['content', 'author_id', 'timestamp'])
