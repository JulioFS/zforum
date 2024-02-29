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

from py4web import action, request, response, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, groups
from .forumhelper import forumhelper as fh


@action('index')
@action.uses('index.html', auth, T)
def index():
    """ /index entry point """
    user = auth.get_user()
    channel_desc = fh.get_system_property('zfss_header_html', '')
    payload = {'channel_desc': channel_desc}
    return payload

@action('zauth/login', method=['get', 'post'])
@action.uses('login.html', auth)
def auth_login():
    """ Custom Login Page """
    req = request
    error = None
    is_cancel = False
    if req.method == 'POST':
        form = req.forms
        email = form.get('email', '')
        passwd = form.get('passwd', '')
        is_cancel = 'cancel' in form.keys()
        # Only call the internal auth methods when it is necessary
        if (len(email) == 0 or len(passwd) == 0):
            error = 'Both email and password must be supplied.'
        else:
            user, error = auth.login(email, passwd)

    # redirect to home if auth was successful, otherwise setup the
    # error message and return back to the login screen
    if (req.method == 'GET' or error is not None) and not is_cancel:
        return {'error': error}
    # Assume Success..
    redirect(URL('index'))

@action('zauth/request_reset_password', method=['get', 'post'])
@action.uses('reset.html', auth)
def auth_request_reset_password():
    """ Custom Request Password Reset """
    error = None
    return {'error': error}
