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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, groups


@action("index")
@action.uses("index.html", auth, T)
def index():
    """ /index entry point """
    user = auth.get_user()
    message = T("Hello {first_name}").format(**user) if user else T("Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    payload = {'message': message, 'actions': actions}
    return payload
