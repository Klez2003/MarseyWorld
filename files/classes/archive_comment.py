import time
from math import floor
from random import randint
from urllib.parse import parse_qs, urlencode, urlparse

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import *

class ArchivedComment(Base):
    pass