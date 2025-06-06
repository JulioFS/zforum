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
from ..common import db, session, T, cache, auth, logger, groups
from ..forumhelper import forumhelper as fh
from pydal.validators import CRYPT

@action('zauth/login', method=['get', 'post'])
@action.uses('zauth/login.html', auth)
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
            # from auth.py, updates the session with the authorized user
            # and acts as a de-facto login
            if user:
                auth.store_user_in_session(user['id'])

    # redirect to home if auth was successful, otherwise setup the
    # error message and return back to the login screen
    if (req.method == 'GET' or error is not None) and not is_cancel:
        return {'error': error, 'email': email}
    # Assume Success..
    return redirect(URL('index'))

@action('zauth/register', method=['get', 'post'])
@action.uses('zauth/register.html')
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
            registration_results = auth.register(payload, validate=False)
            if 'errors' in registration_results and len(
                registration_results['errors'].keys()) > 0:
                for err in registration_results['errors'].values():
                    errors.append(f'<li>{err}</li>')
                error += ''.join(errors) + '</ul>'

    if (req.method == 'GET' or len(errors) > 0) and not is_cancel:
        return {'error': error, 'errors': errors, 'form_fields': payload}
    return redirect(URL('index', vars={'action': '' if is_cancel else 'reg'}))

@action('zauth/request_reset_password', method=['get', 'post'])
@action.uses('zauth/reset.html', auth)
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
    return redirect(URL('index', vars={'action': '' if is_cancel else 'rrp'}))

@action('zauth/profile/<user_id>', method=['get', 'post'])
@action('zauth/profile', method=['get', 'post'])
@action.uses('zauth/profile.html', auth, db, session, T)
def profile(user_id=None):
    """ Main user profile, not entirely similar to OOB """
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
    member_settings_map = {} # {'zfmp_display_name': 1, ...}
    if is_admin and user_id is not None:
        valid_user_id = user_id
    rows = db().select(
        db.member_setting_template.ALL,
        db.member_setting.ALL,
        left=db.member_setting.on(
            (db.member_setting_template.id==db.member_setting.template_id) & \
                (db.member_setting.user_id==valid_user_id)))
    for row in rows:
        member_settings_map[row.member_setting_template.name] = \
            row.member_setting_template.id
        match row.member_setting_template.name:
            case 'zfmp_bio' | 'zfmp_sig':
                form_type = 'text'
            case 'zfmp_allow_pm':
                form_type = 'check'
            case _:
                form_type = 'string'
        available_questions[row.member_setting_template.id] = {
            'template_name': row.member_setting_template.name,
            'description': row.member_setting_template.description,
            'restricted': row.member_setting_template.is_readonly and not \
                is_admin,
            'user_value': '' if row.member_setting.value is None else \
                row.member_setting.value,
            'form_type': form_type
        }
    # Get a list of those channels for which the user is an administrator
    if is_admin:
        admin_channels = db().select(
            db.channel.id,
            db.channel.tag,
            db.channel.title,
            orderby=db.channel.tag)
        admin_channels.compact = False
    else:
        admin_channels = db(db.channel).select(
            join=db.channel_admin.on(
                (db.channel.id==db.channel_admin.channel_id) &
                (db.channel_admin.user_id==valid_user_id) &
                (db.channel_admin.is_active==True)), orderby=db.channel.tag)
    if request.method == 'POST':
        post_code = 0
        form = request.forms
        # If form is posted, it means that either the user requested saving
        # standard properties, or a password change..
        if 'submit-settings' in form:
            update_props = []
            # Update Properties
            for fld in form.keys():
                # Only update those for elements that are member properties,
                # have a valid value, AND if a value exists, to be different
                # from the original default value.
                if fld.startswith('zfmp_') and form[fld].strip() and \
                    available_questions[
                        member_settings_map[fld]]['user_value'] != form[fld]:
                    update_props.append({
                        'prop_id': member_settings_map[fld],
                        'prop_value': form[fld]
                    })
            if update_props:
                fh.put_member_properties(update_props, valid_user_id)
                post_code = 1
        elif 'submit-password-request' in form:
            # Password change request..
            # Verify password and confirm are the same
            # Verify current password is valid
            cur_passwd = form.get('cur-passwd', '')
            new_passwd = form.get('new-passwd', '')
            new_passwd_c = form.get('new-passwd-c', '')
            if new_passwd and new_passwd_c and len(new_passwd) >= 8:
                if new_passwd != new_passwd_c:
                    errors.append('Password and Confirmation do not match.')
            else:
                errors.append('Both new password and confirmation are required, additionally the minimum password '
                              'length is 8 characters.')
            
            if not errors:
                # Both new password and confirmation are valid, now verify that the current password is also valid
                stored_passwd = db(db.auth_user.id==valid_user_id).select(db.auth_user.password).first()
                cur_passwd_crypted = CRYPT()(cur_passwd)[0]
                new_passwd_crypted = CRYPT()(new_passwd)[0]
                if not stored_passwd.password:
                    errors.append('It seems like this account was authenticated using an external provider. '
                                  'Please use the login provider to log in again, or request a password reset.')
                elif cur_passwd_crypted != stored_passwd.password:
                    errors.append('Current password verification failed. Please select your current password again.')
                elif new_passwd_crypted == stored_passwd.password:
                    errors.append('New password and current password are the same.')
                else:
                    # Store the new password..
                    db(db.auth_user.id==valid_user_id).update(password=new_passwd_crypted)
                    post_code = 1

        if not errors:
            redirect(URL(f'zauth/profile/{valid_user_id}',
                         vars={'post_code': post_code}))
    return {
        'is_admin': is_admin,
        'errors': errors,
        'available_questions': available_questions,
        'admin_channels': admin_channels
    }

@action('zauth/system_admin', method=['get', 'post'])
@action.uses('zauth/system_admin.html', auth, db, session, T)
def system_admin():
    """ System Administration Page """
    errors = {}
    payload = {}
    payload_updated = ''
    is_admin = fh.is_sysadmin()
    if not is_admin:
        redirect(URL('ex/unauthorized'))

    # Retrieve the system administration information
    # name, value, description
    system_settings = db().select(
        db.system_setting.ALL, orderby=db.system_setting.name).as_list()

    if request.method == 'POST':
        form = request.forms
        # If form is posted, it means that either the admin requested saving
        # properties (orccancel)
        if 'update-button' in form:
            # Loop through the system_settings, get the appropriate value
            # from the form, and update the record if the values are different
            payload_updated = 'No Updates Required'
            for setting in system_settings:
                if setting['value'] != form.get(setting['name']):
                    rec = db(db.system_setting.name==setting['name']).select().first()
                    rec.update_record(value=form.get(setting['name']))
                    payload_updated = 'System Updated'
        else: # Cancel
            redirect(URL('index'))

    payload['errors'] = errors
    payload['system_updated'] = payload_updated
    payload['system_settings'] = system_settings

    return payload
