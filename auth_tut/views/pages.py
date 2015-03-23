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

import logging
log = logging.getLogger(__name__)

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
    user = User.get_user_by_id(page.owner)
    

    return {
        'page': page,
        'user': user,
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
    user = User.get_user(owner)

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
            page = Page(title=title, uri=Page.websafe_uri(title), owner=user.id, body=body)
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
    page = Page.get_page(uri)
    user = User.get_user_by_id(page.owner)

    try:
        log.debug('Edit page view')
        log.debug(user.groups[0].name)
    except Exception, e:
        log.debug('WARNING: {0}'.format(e))

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
            page.uri = Page.websafe_uri(title)
            DBSession.add(page)
            url = request.route_url('page', title=page.uri)
            return HTTPFound(location=url)

    return {
        'title': title,
        'owner': user.login,
        'body': body,
        'errors': errors,
    }

