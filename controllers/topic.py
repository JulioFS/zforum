"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses generic.html
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n
@action.uses(auth.user)       indicates that the action requires logged in user
@action.uses(auth)            indicates that the action requires auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures})
else your app will result in undefined behavior
"""

import random
from py4web import action, request, response, abort, redirect, URL
from yatl.helpers import A
from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, groups
from ..forumhelper import forumhelper as fh


@action('c/<channel_tag>/topic/new', method=['get', 'post'])
@action.uses('topic_new.html', auth, session, T)
def new_topic(channel_tag):
    """ New Topic, only allowed if the user is authenticated, and either:
    The channel is public
    Or
    Channel is Private and user is member of the channel.
    Or
    User is System/Channel Admin
    """
    user = auth.get_user()
    channel = db(db.channel.tag==channel_tag).select(db.channel.ALL).first()
    is_admin = fh.is_sysadmin()
    is_channel_admin = fh.is_channel_admin(user['id'], channel['id'])
    if not user:
        redirect(URL('ex/unauthorized'))
    if not channel:
        redirect(URL('ex/tagnotfound'))
    if not channel['is_public']:
        # Channel NOT public, you need to be member, or an admin to add topics
    return {}

