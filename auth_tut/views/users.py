from pyramid.response import Response

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden
    )

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from sqlalchemy.exc import DBAPIError

from pyramid.security import (
    authenticated_userid,
    forget,
    remember
)

from auth_tut.models import (
    DBSession,
    User,
    Page,
    )


@view_config(
    route_name='users',
    permission='view',
    renderer='users.mako',
)
def users_view(request):
    users = DBSession.query(User).all()
    return {
        'users': sorted([u.login for u in users])
    }

@view_config(
    route_name='user',
    permission='view',
    renderer='user.mako',
)
def user_view(request):
    user = request.context
    pages = DBSession.query(Page).filter(Page.owner == user.login).all()

    return {
        'user': user,
        'pages': pages,
    }


def validate_user(login, password):
    errors = []

    login = login.strip()
    if not login:
        errors.append('Login may not be empty')
    elif len(login) > 32:
        errors.append('Login may not be longer than 32 characters')

    password = password.strip()
    if not password:
        errors.append('Password may not be empty')

    return {
        'login': login,
        'password': password,
        'errors': errors,
    }


@view_config(
    route_name='create_user',
    renderer='edit_user.mako',
)
def create_user_view(request):
    errors = []
    login = password = ''
    if request.method == 'POST':
        login = request.POST.get('login', '')
        password = request.POST.get('password', '')

        v = validate_user(login, password)
        login = v['login']
        password = v['password']
        errors += v['errors']

        if not errors:
            user = User(login=login, password=password)
            DBSession.add(user)
            url = request.route_url('login')
            return HTTPFound(location=url)

    return {
        'login': login,
        'password': password,
        'errors': errors,
    }
