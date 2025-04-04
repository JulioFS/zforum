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

import os, random, re
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
    """ New Channel Page - Authenticated Users """
    errors = []
    user = auth.get_user()
    if user.get('id', '') == '':
        redirect(URL('ex/unauthorized'))
    form_submitted = request.method == 'POST'
    if form_submitted:
        form = request.forms
        if 'create-button' in form:
            # Even though a channel tag (name) can have any capitalization,
            # no channel  will have the same name.
            # Tag Rules:
            # Any letters, numbers, and any of the following: ()$_. allowed
            tag_rules = re.compile(r'[a-zA-Z0-9()$_.]*$')
            tag = form.get('tag', '').strip() #.lower()
            title = form.get('title', '')
            content = form.get('content', '')
            f_size = int(form.get('fSize', 0))
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
            is_private = form.get('is-private', False) and True
            requires_membership = form.get(
                'requires-membership', False) and True
            if not title:
                errors.append('Title is required.')
            if not content:
                errors.append('Channel description is required.')
            if not tag:
                errors.append('Tag is required.')
            if not errors: # Only run a DB query if it is really needed.
                if tag_rules.match(tag) is None or \
                    profanity.contains_profanity(tag):
                    errors.append(
                        'Tag is invalid, only letters, numbers, and a '
                        'combination of any of ()$_. characters are allowed, '
                        'and must not contain curse word(s).')
                else:
                    # Does the tag exist?
                    tag_exists = db(
                        db.channel.tag.lower() == tag.lower()).count() > 0
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
                    banner=banner,
                    is_private=is_private,
                    requires_membership=requires_membership)
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
    """ Channel Administration via Sys Admin Or Channel Admin """
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
                'title_marked': markdown(channel.title),
                'content': channel.content,
                'content_marked': markdown(channel.content),
                'banner': channel_banner,
                'banner_naked': channel.banner,
                'is_private': channel.is_private,
                'requires_membership': channel.requires_membership
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
                    is_private = form.get('is-private', False) and True
                    requires_membership = form.get(
                        'requires-membership', False) and True
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
                            is_private=is_private,
                            requires_membership=requires_membership)
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
    channel = db(db.channel.tag==tag).select(db.channel.ALL).first()
    if channel:
        # Update the channel "views"
        channel.view += 1
        channel.update_record()
        user = auth.get_user()
        can_admin_channel = False
        if 'id' in user:
            can_admin_channel = fh.is_channel_admin(
                user['id'], channel.id) or fh.is_sysadmin(user['id'])
        # TODO Handle considerations for private/membership channels
        is_private = channel.is_private
        requires_membership = channel.requires_membership
        membership_status = {'has_membership': False, 'is_pending': False}
        if requires_membership:
            # If membership is required, see if you are a member of the channel
            membership_status = fh.get_channel_membership(channel['id'])
        channel_banner = fh.retrieve_channel_banner(
            channel.id, channel.banner)
        channel_info = {
            'id': str(channel.id),
            'tag': channel.tag,
            'title': channel.title,
            'title_marked': markdown(channel.title),
            'content': channel.content,
            'content_marked': markdown(channel.content),
            'banner': channel_banner,
            'is_private': is_private,
            'is_channel_member': membership_status['has_membership'] and not \
                membership_status['is_pending'],
            'is_pending_membership': membership_status['is_pending'],
            'requires_membership': requires_membership,
            'can_admin_channel': can_admin_channel
        }
        payload = {
            'tag': tag,
            'channel_info': channel_info,
            'topics': []
        }
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
    channel.is_private = False
    channel.owner_id is the currently auth user.
    User is a channel admin (via channel_admin.user_id *and is_active*)
    The order of the retrieval should be based on several factors, essentially
    those channels with more topic views and upvotes should be moved higher,
    another option is to order by the last date any of its topics were 
    """
    qry = db.channel.is_private == False
    if fh.is_sysadmin():
        # Don't hide private channels from sysadmins..
        qry = db.channel.id > 0
    all_channels = db(qry).select(db.channel.ALL, orderby=(
        ~db.channel.view | ~db.channel.modified_on))
    channel_list = []
    for c in all_channels:
        channel_list.append({
            'channel': c,
            'title_marked': markdown(c.title),
            'content_marked': markdown(c.content)
        })
    return {
        'channels': channel_list,
        'channel_desc': 'Available Channels.'
    }

@action('channel/request_membership', method=['post'])
@action.uses(auth)
def request_membership():
    """ Receives a request for channel membership optionally
    passing a message to the administrator(s), redirect the user
    back to index with action=req_membership to activate toaster
    massage.
    """
    # Only auth users should ever hit this method
    user = auth.get_user()
    if user:
        form = request.forms
        channel_id = form.get('channel_id', None)
        message = form.get('channel-request-reason', '')
        if channel_id:
            fh.request_channel_membership(channel_id, user['id'])
            # TODO Create message to the channel admins
            # when messaging system is completed.
            #if message:

        url = URL('index', vars={'action': 'req_membership'})
    else:
        url = URL('ex/unauthorized')
    redirect(url)
