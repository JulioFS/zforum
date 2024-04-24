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
from pydal.validators import CRYPT


@action('zauth/login', method=['get', 'post'])
@action.uses('login.html', auth)
def auth_login():
    """ Custom Login Page """
    req = request
    error = None
    is_cancel = False
    email = ''
    if req.method == 'POST':
        form = req.forms
        email = form.get('email', '')
        passwd = form.get('passwd', '')
        is_cancel = 'cancel' in form.keys()
        # Only call the internal auth methods when it is necessary
        if len(email) == 0 or len(passwd) == 0:
            error = 'Both email and password must be supplied.'
        else:
            user, error = auth.login(email, passwd)
            # from auth.py
            if user:
                auth.store_user_in_session(user['id'])

    # redirect to home if auth was successful, otherwise setup the
    # error message and return back to the login screen
    if (req.method == 'GET' or error is not None) and not is_cancel:
        return {'error': error, 'email': email}
    # Assume Success..
    return redirect(URL('index'))

@action('zauth/register', method=['get', 'post'])
@action.uses('register.html')
def auth_regisrer():
    """ Register override """
    req = request
    errors = []
    error = '<p>Please correct the following:</p><ul>'
    is_cancel = False
    payload = {}
    if req.method == 'POST':
        form = req.forms
        is_cancel = 'cancel' in form.keys()
        username = f'zforum-user{str(random.random())[2:]}'
        email = form.get('email', '')
        password = form.get('password', '')
        password_again = form.get('password_again', '')
        first_name = 'zForum'
        last_name = 'Member'
        if len(email) == 0:
            errors.append('<li>Email is required.</li>')
        if len(password) == 0 or len(password_again) == 0 \
            or password != password_again:
            errors.append('<li>Password and Confirmation must match '
                          'and are required.</li>')
        crypt_password = CRYPT()(password)[0]
        payload = {
            'username': username,
            'email': email,
            'password': crypt_password,
            'password_again': crypt_password,
            'first_name': first_name,
            'last_name': last_name
        }
        if len(errors) > 0:
            error += ''.join(errors) + '</ul>'
        else:
            registration_results = auth.register(payload)
            if 'errors' in registration_results and len(
                registration_results['errors'].keys()) > 0:
                for err in registration_results['errors'].values():
                    errors.append(f'<li>{err}</li>')
                error += ''.join(errors) + '</ul>'

    if (req.method == 'GET' or len(errors) > 0) and not is_cancel:
        return {'error': error, 'errors': errors, 'form_fields': payload}
    return redirect(URL('index', vars={'action': '' if is_cancel else 'reg'}))

@action('zauth/request_reset_password', method=['get', 'post'])
@action.uses('reset.html', auth)
def auth_request_reset_password():
    """ Custom Request Password Reset """
    req = request
    error = None
    is_cancel = False
    if req.method == 'POST':
        form = req.forms
        user_email = form.get('username-email', '')
        is_cancel = 'cancel' in form.keys()
        # Only call the internal auth methods when it is necessary
        if len(user_email) == 0:
            error = 'A username or email must be supplied.'
        else:
            # if token is None, the user was not found, but save from
            # notifying the user of this to prevent username leaking
            token = auth.request_reset_password(user_email)  #, route='zauth')
    if (req.method == 'GET' or error is not None) and not is_cancel:
        return {'error': error}
    return redirect(URL('index', vars={'action': 'rrp'}))

@action('zauth/profile/<user_id>', method=['get', 'post'])
@action('zauth/profile', method=['get', 'post'])
@action.uses('profile.html', auth, db, session, T)
def profile(user_id=None):
    """ Main user profile, not entirely similar to OOB """
    req = request
    errors = []
    user = auth.get_user()
    if user is None:
        redirect(URL('ex/unauthorized'))
    
    # If user is authorized, and a user_id user is passed in,
    # the user will be able to edit the passed in user ONLY
    # if the logged in user is an admin..
    is_admin = fh.is_sysadmin()
    valid_user_id = user.get('id')
    available_questions = {}
    if is_admin and user_id is not None:
        valid_user_id = user_id
    rows = db().select(
        db.member_setting_template.ALL,
        db.member_setting.ALL,
        left=db.member_setting.on(
            (db.member_setting_template.id==db.member_setting.template_id) & \
                (db.member_setting.user_id==valid_user_id)))
    for row in rows:
        available_questions[row.member_setting_template.id] = {
            'template_name': row.member_setting_template.name,
            'description': row.member_setting_template.description,
            'can_update': not row.member_setting_template.is_readonly or \
                is_admin,
            'user_value': row.member_setting.value
        }
    if req.method == 'POST':
        # TODO Add logic
        x=1
    return {'errors': errors, 'available_questions': available_questions}
