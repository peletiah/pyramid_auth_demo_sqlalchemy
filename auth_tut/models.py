import urllib

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(Text, unique=True)
    password = Column(Text)
    groups = Column(Text)

    @property
    def __acl__(self):
        return [
            (Allow, self.login, 'view'),
        ]

    def __init__(self, login, password, groups=None):
        self.login = login
        self.password = password
        self.groups = groups or []

    def check_password(self, passwd):
        return self.password == passwd

def get_user(login):
    user = DBSession.query(User).filter(User.login == login).one()
    return user


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
            (Allow, 'g:editor', 'edit'),
        ]

    def __init__(self, title, uri, body, owner):
        self.title = title
        self.uri = uri
        self.body = body
        self.owner = owner

def get_page(key):
    page = DBSession.query(Page).filter(Page.uri == key).one()
    return page


def websafe_uri(txt):
    uri = txt.replace(' ', '-')
    return urllib.quote(uri)


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
        user = get_user(key)
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
        page = get_page(key)
        page.__parent__ = self
        page.__name__ = key
        return page

