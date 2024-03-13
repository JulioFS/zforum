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
@action.uses('new_channel.html', auth, T)
def new_channel():
    """ /index entry point """
    errors = []
    payload = {}
    user = auth.get_user()
    if user is None:
        redirect(URL('exception'))
    form_submitted = request.method == 'POST'
    if form_submitted:
        req = request.forms
        if 'create-button' in req:
            user = auth.get_user()
            tag = req.get('tag', '').strip()
            title = req.get('title', '')
            content = req.get('content', '')
            # TODO Handle image in FS
            # <ombott.request_pkg.helpers.FileUpload object at 0x107ecfc40>
            banner = request.get('channel-img', '')
            # Checkboxes with uncheck state will not be available in
            # request.forms, otherwise it will contain the identifier 'on'
            is_public = req.get('is-public', False) and True
            payload = {
                'user': user,
                'tag': tag,
                'title': title,
                'content': content,
                'banner': banner,
                'is_public': is_public
            }
            if not title:
                errors.append('Title is required.')
            if not content:
                errors.append('Channel description is required.')
            if not tag:
                errors.append('Tag is required.')
            if not errors: # Only run a DB query if it is really needed.
                if tag.find(' ') >= 0 or profanity.contains_profanity(tag):
                    errors.append('Tag is required, must not contain spaces, '
                                  'curse word(s), or invalid name.')
                else:
                    # Does the tag even exist?
                    tag_exists = db(db.channel.tag == tag).count() > 0
                    if tag_exists:
                        errors.append('Tag already exists.')
            if not errors:
                # Create Channel!
                db.channel.insert(
                    tag=tag,
                    title=title,
                    content=content,
                    created_by=user['id'],
                    modified_by=user['id'],
                    owner_id=user['id'],
                    is_public=is_public)
                return redirect(URL(f'c/{tag}', vars={'new': 'true'}))
        else:
            return redirect(URL('index'))

    return {'errors': errors, 'payload': payload}

@action('c/<tag>')
@action.uses('channel_index.html', auth, T)
def channel_index(tag):
    """ Main Index for a channel """
    # Does it exist
    tag_record = db(db.channel.tag == tag).select(db.channel.ALL)
    if tag_record:
        # TODO Handle considerations for private channels
        is_public = tag_record[0].is_public
        channel_info = {
            'title': tag_record[0].title,
            'content': tag_record[0].content,
            'is_public': is_public
        }
        payload = {'tag': tag, 'channel_info': channel_info}
        return payload
    return redirect(URL('ex/tagnotfound'))

@action('c/<tag>/<channel_action>')
def channel_action(tag, channel_action):
    """ GET actions for channel """
    redirect(URL(f'c/{tag}', vars={'subscribed': 'true'}))

@action('channels')
@action.uses('channels.html', auth, T)
def channels():
    """ Retrieves all channels that the user is allowed to
    access, channels that are returned are those in which:
    channel.is_public = True
    channel.owner_id is the currently auth user.
    User is a channel admin (via channel_admin.user_id *and is_active*)
    The order of the retrieval should be based on several factors, essentially
    those channels with more topic views and upvotes should be moved higher,
    another option is to order by the last date any of its topics were 
    """
    # Ok, before we get all fancy, let's return a basic list of channels
    # c/xyz | This is the channel title | 100 Topics | 200 comments
    return {'channels': [1, 2, 3]}