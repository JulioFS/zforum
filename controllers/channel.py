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

import os, random
from better_profanity import profanity
from markdown import markdown
from py4web import action, request, response, abort, redirect, URL
from yatl.helpers import A
from ..common import db, session, T, cache, auth, logger, authenticated, unauthenticated, groups
from ..forumhelper import forumhelper as fh
from ..settings import Z_EXTERNAL_IMAGES, Z_INTERNAL_IMAGES

@action('channel_new', method=['get', 'post'])
@action.uses('channel_new.html', auth, T)
def channel_new():
    """ /index entry point """
    errors = []
    user = auth.get_user()
    if user.get('id', '') == '':
        redirect(URL('ex/unauthorized'))
    form_submitted = request.method == 'POST'
    if form_submitted:
        req = request.forms
        if 'create-button' in req:
            # Channels (tags) will all be lowercase
            tag = req.get('tag', '').strip().lower()
            title = req.get('title', '')
            content = req.get('content', '')
            f_size = int(req.get('fSize', 0))
            # <ombott.request_pkg.helpers.FileUpload object at 0x107ecfc40>
            channel_banner = request.files.get('channel-img', None)
            if channel_banner is not None:
                if f_size > 1500000:
                    errors.append('Upload banner too large, reduce the size'
                                  'and try again.')
                elif not fh.verify_channel_banner(channel_banner):
                    errors.append(
                        'Unable to upload the banner for this channel. '
                        'Only valid image files are allowed.')
            # Checkboxes with uncheck state will not be available in
            # request.forms, otherwise it will contain the identifier 'on'
            is_public = req.get('is-public', False) and True
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
                banner = None
                if channel_banner is not None:
                    banner = channel_banner.filename
                channel_id = db.channel.insert(
                    tag=tag,
                    title=title,
                    content=content,
                    created_by=user['id'],
                    modified_by=user['id'],
                    owner_id=user['id'],
                    banner=banner,
                    is_public=is_public)
                # Store image if available
                if channel_banner is not None:
                    fh.store_channel_banner(channel_id, channel_banner)
                # Make the logged in user the channel admin by default
                fh.grant_channel_admin(channel_id, user['id'])
                return redirect(URL(f'c/{tag}', vars={'new': 'true'}))
        else:
            return redirect(URL('index'))

    return {'errors': errors}

# Admin a channel
@action('channel/admin/<channel_id>', method=['get', 'post'])
@action.uses('channel_admin.html', auth, T)
def channel_admin(channel_id):
    errors = []
    user = auth.get_user()
    if user is None:
        redirect(URL('exception'))
    # User must be a system admin or a channel_admin
    c_admin = fh.is_channel_admin(user['id'], channel_id)
    s_admin = fh.is_sysadmin(user['id'])
    if c_admin or s_admin:
        form_submitted = request.method == 'POST'
        channel = db(db.channel.id==channel_id).select().first()
        if channel:
            channel_banner = fh.retrieve_channel_banner(
                channel.id, channel.banner)
            channel_info = {
                'id': str(channel.id),
                'tag': channel.tag,
                'title': channel.title,
                'content': channel.content,
                'content_marked': markdown(channel.content),
                'banner': channel_banner,
                'banner_naked': channel.banner,
                'is_public': channel.is_public
            }
            if form_submitted:
                # Update channel requested
                form = request.forms
                if 'update-button' in form:
                    # Channels (tags) will all be lowercase
                    title = form.get('title', '')
                    content = form.get('content', '')
                    f_size = int(form.get('fSize', 0))
                    remove_banner_request = form.get('remove-banner', False)
                    # <ombott.request_pkg.helpers.FileUpload object at 
                    # 0x107ecfc40>
                    new_channel_banner = request.files.get('channel-img', None)
                    if new_channel_banner is not None:
                        if f_size > 1500000:
                            errors.append('Upload banner too large, reduce '
                                          'the size and try again.')
                        elif not fh.verify_channel_banner(new_channel_banner):
                            errors.append(
                                'Unable to upload the banner for this channel.'
                                ' Only valid image files are allowed.')
                    # Checkboxes with uncheck state will not be available in
                    # request.forms, otherwise it will contain the identifier 'on'
                    is_public = form.get('is-public', False) and True
                    if not title:
                        errors.append('Title is required.')
                    if not content:
                        errors.append('Channel description is required.')

                    if not errors:
                        # Update Channel!
                        # Default to existing channel banner (if available),
                        # None if not defined..
                        banner_name = channel.banner
                        if new_channel_banner is not None:
                            banner_name = new_channel_banner.filename
                        channel.update_record(
                            title=title,
                            content=content,
                            modified_by=user['id'],
                            banner=banner_name,
                            is_public=is_public)
                        # Store/Replace banner image if available
                        # Remove an existing banner only if you select a new
                        # image and there is an exiting one already or user
                        # selected removal of an existing one and there is an
                        # existing one for sure.
                        if (channel.banner and new_channel_banner) or \
                            (channel.banner and remove_banner_request):
                            cur_banner_filename = os.path.join(
                                Z_EXTERNAL_IMAGES,
                                'channels',
                                str(channel_id),
                                channel.banner)
                            if os.path.isfile(cur_banner_filename):
                                os.unlink(cur_banner_filename)
                        if new_channel_banner is not None:
                            fh.store_channel_banner(
                                channel_id,
                                new_channel_banner)
                    if errors:
                        return {
                            'channel_info': channel_info,
                            'errors': errors
                        }
                # Back to channel.
                redirect(URL(f'c/{channel.tag}'))
            else:
                # "HTTP GET", display edit form with defaults..
                return {
                    'channel_info': channel_info,
                    'errors': errors
                }
        else:
            redirect(URL('ex/tagnotfound'))
    else:
        redirect(URL('ex/unauthorized'))

# Main Channel Index
@action('c/<tag>')
@action.uses('channel_index.html', auth, T)
def channel_index(tag):
    """ Main Index for a channel """
    # Does it exist
    z_channel = db(db.channel.tag == tag).select(db.channel.ALL).first()
    if z_channel:
        user = auth.get_user()
        can_admin_channel = False
        if 'id' in user:
            can_admin_channel = fh.is_channel_admin(
                user['id'], z_channel.id) or fh.is_sysadmin(user['id'])
        # TODO Handle considerations for private channels
        is_public = z_channel.is_public
        channel_banner = fh.retrieve_channel_banner(
            z_channel.id, z_channel.banner)
        channel_info = {
            'id': str(z_channel.id),
            'tag': z_channel.tag,
            'title': z_channel.title,
            'content': z_channel.content,
            'content_marked': markdown(z_channel.content),
            'banner': channel_banner,
            'is_public': is_public,
            'can_admin_channel': can_admin_channel
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
    all_channels = db().select(db.channel.ALL, orderby=db.channel.modified_on)
    return {
        'channels': all_channels,
        'channel_desc': 'Available Channels.'
    }
