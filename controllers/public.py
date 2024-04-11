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


@action('index')
@action.uses('index.html', auth, db, session, T)
def index():
    """ /index entry point """
    #groups.add(1, 'manager')
    #user = auth.get_user()
    channel_desc = fh.get_system_property('zfss_header_html', '')
    is_systemadmin = fh.is_sysadmin()
    payload = {'channel_desc': channel_desc, 'is_systemadmin': is_systemadmin}
    return payload

@action('ex/<err>')
@action.uses('exception.html')
def exception(err):
    """ Handles handled exceptions (controlled) """
    error_message = 'Unknown Exception.'
    if err:
        if err == 'unauthorized':
            error_message = ('Not authorized to access this resource, '
                             'please contact the forum administrator.')
        elif err == 'tagnotfound':
            error_message = ('Unable to find the selected channel '
                             'or you do not have the proper access.')
    return {'error': error_message}
