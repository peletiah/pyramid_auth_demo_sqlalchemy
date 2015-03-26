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

@forbidden_view_config()
def forbidden_view(request):
    # do not allow a user to login if they are already logged in
    if authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)

@view_config(
    route_name='home',
    renderer='home.mako',
)
def home_view(request):
    login = authenticated_userid(request)
    if login:
        user = DBSession.query(User).filter(User.login == login).one()
    else:
        user = None
    try:
        user_pages = DBSession.query(Page).filter(Page.owner == user.id).all()
    except:
        user_pages = None

    return {
        'user': user,
        'user_pages': user_pages,
        'request': request,
    }

@view_config(
    route_name='login',
    renderer='login.mako',
)
def login_view(request):
    next = request.params.get('next') or request.route_url('home')
    login = ''
    did_fail = False
    users = DBSession.query(User).all()
    if 'submit' in request.POST:
        login = request.POST.get('login', '')
        passwd = request.POST.get('passwd', '')

        user = User.get_user(login)
        if user and user.validate_password(passwd):
            headers = remember(request, login)
            return HTTPFound(location=next, headers=headers)
        did_fail = True

    return {
        'login': login,
        'next': next,
        'failed_attempt': did_fail,
        'users': users,
        'request': request
    }

@view_config(
    route_name='logout',
)
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)


