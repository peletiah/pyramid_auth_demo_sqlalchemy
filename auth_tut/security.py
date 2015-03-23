from .models import (
    DBSession,
    User,
    Page,
    )


import logging
log = logging.getLogger(__name__)


def auth_callback(login, request):
    log.debug('auth_callback called with USER: {0}'.format(login))
    user = User.get_user(login)
    if user and user.groups:
        group_list = ['g:%s' % g.name for g in user.groups]
        log.debug('auth_callback found GROUPS: {0} for USER: {1}'.format(group_list, login))
        return group_list
    elif user:
        log.debug('auth_callback found USER: {0}'.format(user))
        return [user.id]
    else:
        log.debug('auth_callback found no authentication credentials')
        return []
