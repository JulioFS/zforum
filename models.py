"""
zForum database model.
"""

import datetime
#from pydal.validators import *
from .common import db, Field

now = datetime.datetime.utcnow

# Rank: A measurement of how "important" the channel is for display
# Rank = channel views (15%) + topics in it (50%) + responses to topics (35%)
# Examples:
# Channel 1: 10 views, 5 Topics, 20 Resp: (10*.15) + (5*.5) + (20*.35) = 11
# Channel 2: 7 views, 15 Topics, 5 resp: (7*.15) + (15*.5) + (5*.35) = 10.3
# If channel is_private, then it won't show in search results, it will still
#   be ranked.
# If channel requires_membership, it means that, regadless if it is_private
#   the auth user will require membership to add/reply to topics.
db.define_table(
    'channel',
    Field('tag', type='string', length=64), # Must Index
    Field('banner', type='string', length=128),
    Field('title', type='string', required=True, length=128),
    Field('content', type='text'),
    Field('view', type='integer', default=0),
    Field('rank', type='decimal(10,2)', default=0.0),
    Field('created_by', 'reference auth_user'),
    Field('created_on', type='datetime', default=now),
    Field('modified_by', 'reference auth_user' ),
    Field('modified_on', type='datetime', default=now, update=now),
    Field('is_private', type='boolean', default=False),
    Field('requires_membership', type='boolean', default=False),
    Field('is_banned', type="boolean", default=False)
)
db.commit()

# A channel_membership record will be necessary for a user if the channel
# requires_membership (independent if the channel is_private or not),
# Users visiting these type of channels will have the option to "request"
# a membership to the channel admin
db.define_table(
    'channel_membership',
    Field('user_id', 'reference auth_user'),
    Field('channel_id', 'reference channel'),
    Field('is_new_request', type='boolean', default=True),
    Field('expires_on', type='datetime'),
    Field('created_by', 'reference auth_user'),
    Field('created_on', type='datetime', default=now),
    Field('modified_by', 'reference auth_user' ),
    Field('modified_on', type='datetime', default=now, update=now)
)
db.commit()

# A channel subscription just means that the user has "favorited" the
# Channel, the user would still need to have a membership to add/reply
# posts in the channel if it requires_membership
db.define_table(
    'channel_subscription',
    Field('channel_id', 'reference channel'),
    Field('user_id', 'reference auth_user'),
    Field('is_active', type='boolean', default=True),
    Field('created_by', 'reference auth_user'),
    Field('created_on', type='datetime', default=now)
)
db.commit()

db.define_table(
    'channel_admin',
    Field('user_id', 'reference auth_user'),
    Field('channel_id', 'reference channel'),
    Field('is_active', type='boolean', default=True)
)
db.commit()

# This table contains both topic and responses, with is_parent properly
# identifying the topic as 'parent', and parent_id (being not null)
# identifying (a) being a child, and (b) of which main topic
db.define_table(
    'topic',
    Field('channel_id', 'reference channel'),
    # Title is not required for topic responses, enforce in code/UI
    Field('title', type='string', length=128),
    Field('content', type='text', required=True),
    Field('is_readonly', type='boolean', default=False),
    # If is_visible = False, then only admins can see it:
    Field('is_visible', type='boolean', default=True),
    Field('is_promoted', type='boolean', default=False), # Top of the channel
    Field('is_parent', type='boolean', required=True),
    # if is_system==True, display on main page
    Field('is_system_', type='boolean'),
    Field('view', type='integer'),
    Field('upvote', type='integer'),
    Field('parent_id', type='integer'),
    Field('created_on', type='datetime', default=now),
    Field('modified_on', type='datetime', default=now, update=now),
    Field('created_by', 'reference auth_user'),
    Field('modified_by', 'reference auth_user')
)
db.commit()

db.define_table(
    'message_categories',
    Field('name', type='string', required=True, length=128),
    Field('display_order', type='integer')
)
db.commit()

db.define_table(
    'message',
    Field('category_id', 'reference message_categories'),
    Field('is_read', type='boolean', default=False),
    Field('user_id', 'reference auth_user'),
    Field('from_user_id', 'reference auth_user'),
    Field('subject', type='string', length=128, required=True),
    Field('message', type='text', required=True),
    Field('created_on', type='datetime', default=now)
)
db.commit()

# E.g. ['initial_message': 'Welcome {user} to the new system']
db.define_table(
    'system_message_template',
    Field('key', type='string', length=64, required=True),
    Field('content', type='string', length=128, required=True)
)
db.commit()

db.define_table(
    'system_setting',
    Field('name', type='string', length=64, required=True),
    Field('value', type='string', length=128),
    Field('description', length=128)
)
db.commit()

db.define_table(
    'inappropriate_topic',
    Field('topic_id', 'reference topic'),
    Field('created_on', type='datetime', default=now),
    Field('created_by', 'reference auth_user')
)
db.commit()

db.define_table(
    'subscription',
    Field('user_id', 'reference auth_user'),
    Field('topic_id', 'reference topic'),
    Field('is_active', type='boolean', default=True)
)
db.commit()

db.define_table(
    'rank',
    Field('name', type='string', length=128, required=True),
    Field('min_value', type='integer', notnull=True)
)
db.commit()

db.define_table(
    'member_setting_template',
    Field('name', required=True, notnull=False),
    Field('description', required=True, notnull=False),
    Field('is_readonly', type='boolean', notnull=False)
)
db.commit()

db.define_table(
    'member_setting',
    Field('user_id', 'reference auth_user'),
    Field('template_id', 'reference member_setting_template'),
    Field('value', type='text', length=128)
)
db.commit()

db.define_table(
    'member_avatar',
    Field('user_id', 'reference auth_user'),
    Field('avatar', type='text'),
    Field('content_type', type='string', length=128)
)
db.commit()

# []'en/US', 'English (US)']
db.define_table(
    'available_languages',
    Field('code', notnull=True),
    Field('description', type='string', length=128, notnull=True)
)
db.commit()

# Images will be stored in the filesystem, a hash will be
# created to identity the location of the files (https://techfuel.net/story/3)
# implemented in forumhelper.py
db.define_table(
    'topic_image',
    Field('topic_id', 'reference topic'),
    Field('image_hash', type='string', length=256, notnull=True)
)
db.commit()

# Miscellaneous error messages
db.define_table(
    'error_messages',
    Field('message_key', type='string', length=64, notnull=False),
    Field('description', type='string', length=256, notnull=False)
)
db.commit()

# Some tables must have necessary information for the system to operate
# correctly, verify that this is the case and populate the appropriate
# tables if needed:

# System Error Messages
if db(db.error_messages).isempty():
    error_messages = [
        {'unauthorized', 'Not authorized to access this resource, please '
         'contact the forum administrator.'
        },
        {'tagnotfound', 'Unable to find the selected channel '
         'or you do not have the proper access.'
        }
    ]
    db.error_messages.bulk_insert(error_messages)
    db.commit()

# Personal Messages:
if db(db.message_categories).isempty():
    categories = [
        {
            'zfpm_display_order' : 1,
            'name' : 'Inbox'
        },
        {
            'zfpm_display_order' : 2,
            'name' : 'Read'
        },
        {
            'zfpm_display_order' : 3,
            'name' : 'Sent'
        },
        {
            'zfpm_display_order' : 4,
            'name' : 'Trash'
        }
    ]
    db.message_categories.bulk_insert(categories)
    db.commit()

# System Settings
if db(db.system_setting).isempty():
    system_settings = [
        {
            'name' : 'zfss_topic_teaser_length',
            'description' : ('Topic Teaser Length: The number of characters '
                            'shown for a topic when it is viewed from the '
                               'topic listing page'),
            'value' : '300'
        },
        {
            'name' : 'zfss_allow_member_avatars',
            'description' : ('Allow Avatars: If empty, users will not be '
                               'given the choice of adding or change their '
                               'avatars, any other value will enable avatars '
                               'for all registered users in the system'),
            'value' : 'True'
        },
        {
            'name' : 'zfss_system_language',
            'description' : ('System Language: This value will be used when '
                              'a user accesses the system (Anonymous User), '
                              'once the user is signed in, they will have '
                              'the opportunity of changing the language '
                              'settings for their sessions. The language '
                              'code must match any of the languages defined '
                              'in the Available Languages section.'),
            'value' : 'en_US'
        },
        {
            'name' : 'zfss_admin_contact_email',
            'description' : ('Admin Contact: (Important) - The forum '
                               'system uses this value to specify the *From* '
                               'email header for any email that is sent out, '
                               'please use a valid email address that your '
                               'domain will recognize, otherwise your '
                               'system may not send emails at all.'),
            'value' : 'admin@techfuel.net'
        },
        {
            'name' : 'zfss_use_ranking_system',
            'description' : ('Use Ranking System: If empty, the forum '
                               'will use default values of Member, Channel '
                               'Administrator or System Administrator, any '
                               'other value will enable forum rankings based '
                               'on the number of postings the users have '
                               '(see table member_rank for rank information.)'),
            'value' : 'True'
        },
        {
            'name' : 'zfss_hot_topic_threshold',
            'description' : ('Hot Topic Threshold: Number of views '
                               'necessary to mark the topic as *hot*.'),
            'value' : '300'
        },
        {
            'name' : 'zfss_member_quota',
            'description' : ('Message Quota: Leave empty to disable '
                               'quotas for messages for your users, any other '
                               'numeric value will represent the number '
                               'of <b>bytes</b> of allowance, an invalid '
                               'amount will always default to 50Kb per user.'),
            'value' : '50000'
        },
        {
            'name' : 'zfss_system_announcement_max',
            'description' : ('System Announcements View: This controls the '
                               '(maximum) number of system announcements that '
                               'zForum will display in its right nav, an '
                               'invalid value or zero will show a =-No '
                               'System Messages-= title.'),
            'value' : '10'
        },
        {
            'name' : 'zfss_latest_postings_max',
            'description' : ('Latest Postings View: This controls the '
                               '(maximum) number of latest postings that '
                               'zForum will display in its right nav, '
                               'an invalid value or zero will show '
                               'a =-No Messages-= title.'),
            'value' : '10'
        },
        {
            'name' : 'zfss_responses_per_page',
            'description' : ('Responses per page: Controls the amount of '
                               'responses (children topics) that zForum '
                               'will show and will add pagination/lazy '
                               'loading accordingly.'),
            'value' : '15'
        },
        {
            'name' : 'zfss_header_html',
            'description' : ('Header Text: This can contain html/markdown '
                               'code and will be shown at the top-bar of '
                               'zForum.'),
            'value' : ('### Welcome to zForum - A lightweight, no-ads forum '
                       'system')
        },
        {
            'name' : 'zfsp_available_languages',
            'description' : ('Available languages to the user, use '
                               'the form: Language:languagecode_COUNTRYCODE, '
                               '(e.g. US English:en_US). Separate each '
                               'set by the PIPE Symbol (|).'),
            'value' : ('English (U.S.A):en_US|Spanish (México):es_MX|'
                       'Dutch (Nederlands):nl_NL|French (France):fr_FR')
        }
    ]

    db.system_setting.bulk_insert(system_settings)
    db.commit()

if db(db.rank).isempty():
    ranks = [
        {
            'name' : 'Starfleet Ensign',
            'min_value' : 0
        },
        {
            'name' : 'Starfleet Lieutenant, Junior Grade',
            'min_value' : 6
        },
        {
            'name' : 'Starfleet Lieutenant',
            'min_value' : 15
        },
        {
            'name' : 'Starfleet Lieutenant Commander',
            'min_value' : 40
        },
        {
            'name' : 'Starfleet Commander',
            'min_value' : 85
        },
        {
            'name' : 'Starfleet Captain',
            'min_value' : 110
        },
        {
            'name' : 'Starfleet Commodore',
            'min_value' : 160
        },
        {
            'name' : 'Starfleet Rear Admiral',
            'min_value' : 200
        },
        {
            'name' : 'Starfleet Vice Admiral',
            'min_value' : 250
        },
        {
            'name' : 'Starfleet Admiral',
            'min_value' : 500
        },
        {
            'name' : 'Starfleet Fleet Admiral',
            'min_value' : 1000
        }
    ]
    db.rank.bulk_insert(ranks)
    db.commit()

if db(db.member_setting_template).isempty():
    settings = [
        {
            'name': 'zfmp_display_name',
            'description': 'Display/screen name (call-sign, handle, etc.)',
            'is_readonly': False
        },
        {
            'name': 'zfmp_bio',
            'description': 'About self (text only)',
            'is_readonly': False
        },
        {
            'name': 'zfmp_allow_pm',
            'description': 'Allow to be contacted by other members',
            'is_readonly': False
        },
        {
            'name': 'zfmp_sig',
            'description': 'Append this at the end of posts/comments',
            'is_readonly': False
        },
        {
            'name': 'zfmp_url',
            'description': 'Personal/business, social media website',
            'is_readonly': False
        },
        {
            'name': 'zfmp_last_login',
            'description': 'User last login date',
            'is_readonly': True
        },
        {
            'name': 'zfmp_last_login_ip',
            'description': 'User last login IP',
            'is_readonly': True
        },
        {
            'name': 'zfmp_posts',
            'description': 'Number of posts',
            'is_readonly': True
        },
        {
            'name': 'zfmp_replies',
            'description': 'Number of replies',
            'is_readonly': True
        },
        {
            'name': 'zfmp_joined',
            'description': 'Date joined',
            'is_readonly': True
        }
    ]
    db.member_setting_template.bulk_insert(settings)
    db.commit()
