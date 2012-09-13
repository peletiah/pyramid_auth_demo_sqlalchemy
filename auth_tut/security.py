from .models import (
    DBSession,
    User,
    Page,
    )


def groupfinder(userid, request):
    user = DBSession.query(User).filter(User.login == userid).one()
    if user and user.groups:
        return ['g:%s' % g for g in user.groups.split(',')]
    else:
        return []
