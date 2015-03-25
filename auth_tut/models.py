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

from passlib.hash import pbkdf2_sha256

import logging
log = logging.getLogger(__name__)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

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
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        hash = pbkdf2_sha256.encrypt(password)
        self.password = hash

    def validate_password(self, password):
        """Check a password against an existing hash."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        hash = self.password
        log.debug(password)
        return pbkdf2_sha256.verify(password, hash)
        
    @classmethod
    def get_user(self,login):
        try:
            user = DBSession.query(User).filter(User.login == login).one()
            return user
        except Exception, e:
            print 'Error retrieving user %s: ',e
            return None
    
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

    @property
    def __acl__(self): 

        # only allow members of this group to add new members
        access_list = [(Allow, 'g:{0}'.format(self.name), 'edit')]
        log.debug('GROUP access list: {0}'.format(access_list))
        return access_list

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_group(self, name):
        log.debug(name)
        group = DBSession.query(Group).filter(Group.name == name).one()
        return group


class Page(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    uri = Column(Text, unique=True)
    body = Column(Text)
    owner = Column('owner', Integer, ForeignKey('users.id', onupdate="CASCADE", ondelete="CASCADE"))

    @property
    def __acl__(self): 

        log.debug('Owner: {0}'.format(self.owner))
        access_list = [
            (Allow, self.owner, 'edit'),
        ]

        user = User.get_user_by_id(self.owner)
        for group in user.groups:
            access_list.append((Allow, 'g:{0}'.format(group.name), 'edit'))

        return access_list

 
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
        (Allow, Everyone, 'view'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        user = User.get_user(key)
        user.__parent__ = self
        user.__name__ = key
        return user

class GroupFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'create'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        group = Group.get_group(key)
        group.__parent__ = self
        group.__name__ = key
        return group

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

