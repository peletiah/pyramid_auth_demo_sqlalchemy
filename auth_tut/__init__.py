from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from auth_tut.security import groupfinder

from auth_tut.models import (
    RootFactory as RootFactory,
    UserFactory as UserFactory,
    PageFactory as PageFactory
)

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    authn_policy = AuthTktAuthenticationPolicy(
        secret=settings['auth_tut.secret'],
        callback=groupfinder
    )
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        root_factory=RootFactory,
    )
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('users', '/users', factory=UserFactory)
    config.add_route('user', '/user/{login}', factory=UserFactory,
                     traverse='/{login}')

    config.add_route('pages', '/pages', factory=PageFactory)
    config.add_route('create_page', '/create_page', factory=PageFactory)
    config.add_route('page', '/page/{title}', factory=PageFactory,
                     traverse='/{title}')
    config.add_route('edit_page', '/page/{title}/edit', factory=PageFactory,
                     traverse='/{title}')
    config.scan()
    return config.make_wsgi_app()

