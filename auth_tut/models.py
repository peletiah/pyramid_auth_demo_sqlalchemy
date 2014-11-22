import urllib
import os

from sqlalchemy import (
    Table,
    Column,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
    Unicode
    )

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    authenticated_userid,
    forget,
    remember,
    ALL_PERMISSIONS
    )

import hashlib
from auth_tut.helpers.pbkdf2.pbkdf2 import pbkdf2_bin
from os import urandom
from base64 import b64encode, b64decode
from itertools import izip


import logging
log = logging.getLogger(__name__)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
# Linear to the hashing time. Adjust to be high but take a reasonable
# amount of time on your server. Measure with:
# python -m timeit -s 'import passwords as p' 'p.make_hash("something")'
COST_FACTOR = 10000

user_group_table = Table('user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('user_id', 'group_id', name='user_id_group_id'))



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(Text, unique=True)
    password = Column(Unicode(80), nullable=False)
    groups = relationship('Group', secondary=user_group_table, backref='memberships')

    @property
    def __acl__(self):
        return [
            (Allow, self.login, 'view'),
        ]

    def __init__(self, login, password):
        self.login = login
        self._make_hash(password)


    def _make_hash(self, password):
        """Generate a random salt and return a new hash for the password."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = b64encode(urandom(SALT_LENGTH))
        hashed_password =  'PBKDF2$%s$%i$%s$%s' % (
            HASH_FUNCTION,
            COST_FACTOR,
            salt,
            b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                                 getattr(hashlib, HASH_FUNCTION))))

        self.password = hashed_password

    def validate_password(self, password):
        """Check a password against an existing hash."""
        log.debug(password)
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        algorithm, hash_function, cost_factor, salt, hash_a = self.password.split('$')
        assert algorithm == 'PBKDF2'
        hash_a = b64decode(hash_a)
        hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                            getattr(hashlib, hash_function))
        assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
        # Same as "return hash_a == hash_b" but takes a constant time.
        # See http://carlos.bueno.org/2011/10/timing.html
        diff = 0
        for char_a, char_b in izip(hash_a, hash_b):
            diff |= ord(char_a) ^ ord(char_b)
        return diff == 0

    def _set_password(self, password):
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self.password = hashed_password

    @classmethod
    def get_user(self,login):
        user = DBSession.query(User).filter(User.login == login).one()
        return user
    
    @classmethod
    def get_users(self):
        users = DBSession.query(User).all()
        return users
    
    
    @classmethod
    def get_user_by_id(self,user_id):
        user = DBSession.query(User).filter(User.id == user_id).one()
        return user

    @classmethod
    def get_user_by_login(self,user_login):
        user = DBSession.query(User).filter(User.login == user_login).one()
        return user



class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    users = relationship('User', secondary=user_group_table, backref='members')

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_group(self, name):
        group = DBSession.query(Group).filter(Group.name == name).one()
        return group


class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    uri = Column(Text, unique=True)
    body = Column(Text)
    owner = Column(Text)

    @property
    def __acl__(self):
        return [
            (Allow, self.owner, 'edit'),
        ]

    def __init__(self, title, uri, body, owner):
        self.title = title
        self.uri = uri
        self.body = body
        self.owner = owner

    @classmethod
    def get_page(self, key):
        page = DBSession.query(Page).filter(Page.uri == key).one()
        return page
    
    
    @classmethod
    def websafe_uri(self, txt):
        uri = txt.replace(' ', '-')
        return urllib.quote(uri.encode('utf-8'))

class RootFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

class UserFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        user = User.get_user(key)
        user.__parent__ = self
        user.__name__ = key
        return user

class PageFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'create'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        page = Page.get_page(key)
        page.__parent__ = self
        page.__name__ = key
        return page

