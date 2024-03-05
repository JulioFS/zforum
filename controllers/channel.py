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
from profanity import profanity
from py4web import action, request, response, abort, redirect, URL
from yatl.helpers import A
from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, groups
from ..forumhelper import forumhelper as fh

@action('new_channel', method=['get', 'post'])
@action.uses('new_channel.html', auth.user, T)
def new_channel():
    """ /index entry point """
    errors = []
    payload = {}
    form_submitted = request.method == 'POST'
    if form_submitted:
        req = request.forms
        if 'create-button' in req:
            user = auth.get_user()
            tag = req.get('tag', None)
            title = req.get('title', None)
            content = req.get('content', None)
            banner = req.get('channel-img', None)
            is_public = req.get('is-public', None)
            if title is None:
                errors.append('Title is required.')
            if content is None:
                errors.append('Content is required.')
            if tag is None:
                errors.append('Tag is required.')
            if not errors: # Only run a DB query if it is really needed.
                if tag.find(' ') >= 0 or profanity.contains_profanity(tag):
                    errors.append('Tag is required, must not contain spaces, '
                                  'or contain a curse word.')
                else:
                    # Does the tag even exist?
                    tag_exists = db(db.channel.tag == tag).count() > 0
                    if tag_exists:
                        errors.append('Tag already exists.')
            if not errors:
                # Create Channel!
                errors.append('Channel Created!')
                return redirect(URL(f'c/{tag}'))
        else:
            return redirect(URL('index'))

    return {'errors': errors, 'payload': payload}

@action('c/<tag>')
@action.uses('channel_index.html', auth, T)
def channel_index(tag):
    """ Main Index for a channel """
    return {}
