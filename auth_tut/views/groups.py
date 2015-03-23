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
    Group,
    )

import logging
log = logging.getLogger(__name__)



@view_config(
    route_name='groups',
    permission='view',
    renderer='groups.mako',
)
def groups_view(request):
    groups = DBSession.query(Group).all()
    return {
        'groups': groups,
    }


@view_config(
    route_name='create_group',
    permission='create',
    renderer='edit_group.mako',
)
def create_group_view(request):
    errors = []
    name = ''
    member_list = list()
    users = User.get_users()
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        members_post = request.POST.getall('member')

        if not errors:
            group = Group(name=name)
            DBSession.add(group)
            for user in users:
                if user.login in members_post:
                    group.users.append(user)
            url = request.route_url('home')
            return HTTPFound(location=url)

    return {
        'name': name,
        'users': users,
        'member_list': member_list,
        'errors': errors,
    }

@view_config(
    route_name='edit_group',
    permission='edit',
    renderer='edit_group.mako',
)
def edit_group_view(request):
    name = request.matchdict['name']
    group = Group.get_group(name)
    users = User.get_users()
    member_list = list()
    for member in group.users:
        member_list.append(member.login)

    errors = []
    if request.method == 'POST':
        name = request.POST.get('name', '')
        members_post = request.POST.getall('member')
        if authenticated_userid(request) not in members_post:
            log.debug('AUTHENTICATED USERID NOT IN MEMBERS_POST')
            errors.append('Can\'t remove yourself from this group')
            log.debug(errors)

        if not errors:
            for user in users:
                if user.login in members_post:
                    group.users.append(user)
                elif user.login in member_list and user.login not in members_post:
                    group.users.remove(user)
            group.name = name
            url = request.route_url('groups')
            return HTTPFound(location=url)
         
    return {
        'name': name,
        'users': users,
        'member_list': member_list,
        'errors': errors,
    }


