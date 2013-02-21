from .models import (
    DBSession,
    User,
    Page,
    )


def groupfinder(userid, request):
    user = User.get_user(userid)
    if user and user.groups:
        return ['g:%s' % g.name for g in user.groups]
    else:
        return []
