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

from markdown import markdown
from py4web import action
from ..common import db, session, auth
from ..forumhelper import forumhelper as fh


@action('index')
@action.uses('pub/index.html', auth, session)
def index():
    """ /index entry point """
    #groups.add(1, 'manager')
    #user = auth.get_user()
    channel_desc = fh.get_system_property('zfss_header_html', '')
    user_info = fh.get_user_info()
    payload = {
        'channel_desc': markdown(channel_desc),
        'user_info': user_info
    }
    return payload

@action('ex/<err>')
@action.uses('pub/exception.html', db)
def exception(err):
    """ Handles handled exceptions (controlled) """
    default_error = f'Unknown Exception: ${err}'
    error_message = db(
        db.error_messages.message_key==err).select(
            db.error_messages.description).first().get(
                'description', default_error)
    return {'error': error_message}
