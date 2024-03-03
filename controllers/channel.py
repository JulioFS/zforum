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

@action('new-channel')
@action.uses('new-channel.html', auth.user, T)
def new_channel():
    """ /index entry point """
    user = auth.get_user()
    payload = {}
    return payload
