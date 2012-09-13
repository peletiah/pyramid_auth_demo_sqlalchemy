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

from .models import (
    DBSession,
    User,
    Page,
    get_user,
    get_page,
    websafe_uri
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
    user = DBSession.query(User).filter(User.login == login).first()
    user_pages = DBSession.query(Page).filter(Page.owner == login).all()

    return {
        'user': user,
        'user_pages': user_pages,
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

        user = get_user(login)
        if user and user.check_password(passwd):
            headers = remember(request, login)
            return HTTPFound(location=next, headers=headers)
        did_fail = True

    return {
        'login': login,
        'next': next,
        'failed_attempt': did_fail,
        'users': users,
    }

@view_config(
    route_name='logout',
)
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)

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

@view_config(
    route_name='pages',
    permission='view',
    renderer='pages.mako',
)
def pages_view(request):
    pages = DBSession.query(Page).all()
    return {
        'pages': pages,
    }

@view_config(
    route_name='page',
    permission='view',
    renderer='page.mako',
)
def page_view(request):
    page = request.context

    return {
        'page': page,
    }

def validate_page(title, body):
    errors = []

    title = title.strip()
    if not title:
        errors.append('Title may not be empty')
    elif len(title) > 32:
        errors.append('Title may not be longer than 32 characters')

    body = body.strip()
    if not body:
        errors.append('Body may not be empty')

    return {
        'title': title,
        'body': body,
        'errors': errors,
    }

@view_config(
    route_name='create_page',
    permission='create',
    renderer='edit_page.mako',
)
def create_page_view(request):
    owner = authenticated_userid(request)

    errors = []
    body = title = ''
    if request.method == 'POST':
        title = request.POST.get('title', '')
        body = request.POST.get('body', '')

        v = validate_page(title, body)
        title = v['title']
        body = v['body']
        errors += v['errors']

        if not errors:
            page = Page(title=title, uri=websafe_uri(title), owner=owner, body=body)
            DBSession.add(page)
            url = request.route_url('page', title=page.uri)
            return HTTPFound(location=url)

    return {
        'title': title,
        'owner': owner,
        'body': body,
        'errors': errors,
    }
@view_config(
    route_name='edit_page',
    permission='edit',
    renderer='edit_page.mako',
)
def edit_page_view(request):
    uri = request.matchdict['title']
    page = get_page(uri)

    errors = []
    title = page.title
    body = page.body
    if request.method == 'POST':
        title = request.POST.get('title', '')
        body = request.POST.get('body', '')

        v = validate_page(title, body)
        title = v['title']
        body = v['body']
        errors += v['errors']

        if not errors:
            page.title = title
            page.body = body
            page.uri = websafe_uri(title)
            DBSession.add(page)
            url = request.route_url('page', title=page.uri)
            return HTTPFound(location=url)

    return {
        'title': title,
        'owner': page.owner,
        'body': body,
        'errors': errors,
    }

