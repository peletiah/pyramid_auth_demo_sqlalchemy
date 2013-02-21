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
    renderer='edit_group.mako',
)
def create_group_view(request):
    errors = []
    name = ''
    members_db = list()
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
        'members_db': members_db,
        'errors': errors,
    }

@view_config(
    route_name='edit_group',
    renderer='edit_group.mako',
)
def edit_group_view(request):
    name = request.matchdict['name']
    group = Group.get_group(name)
    users = User.get_users()
    members_db = list()
    for member in group.users:
        members_db.append(member.login)

    errors = []
    if request.method == 'POST':
        name = request.POST.get('name', '')
        members_post = request.POST.getall('member')

        if not errors:
            for user in users:
                if user.login in members_post:
                    group.users.append(user)
                elif user.login in members_db and user.login not in members_post:
                    group.users.remove(user)
            url = request.route_url('home')
            return HTTPFound(location=url)
         
    return {
        'name': name,
        'users': users,
        'members_db': members_db,
        'errors': errors,
    }


