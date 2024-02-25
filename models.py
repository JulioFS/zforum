"""
ZForum database model.
"""

import datetime
#from pydal.validators import *
from .common import db, Field

now = datetime.datetime.utcnow

db.define_table(
    'channel',
    Field('tag', type='string', length=64), # Must Index
    Field('title', type='string', required=True, length=128),
    Field('content', type='text'),
    Field('created_by', 'reference auth_user'),
    Field('created_on', type='datetime', default=now),
    Field('modified_by', 'reference auth_user' ),
    Field('modified_on', type='datetime', default=now, update=now),
    Field('owner_id', 'reference auth_user'),
    Field('is_public', type='boolean', default=True)
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
    Field('display_order', type='number')
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
    Field('Name', type='string', length=128, required=True),
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

# Some tables must have necessary information for the system to operate
# correctly, verify that this is the case and populate the appropriate
# tables if needed:

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

# System Settings
if db(db.system_setting).isempty():
    system_settings = [
        {
            'property_name' : 'zfss_topic_teaser_length',
            'property_desc' : ('Topic Teaser Length: The number of characters '
                               'shown for a topic when it is viewed from the '
                               'topic listing page')
        },
        {
            'property_name' : 'zfss_allow_member_avatars',
            'property_desc' : ('Allow Avatars: If empty, users will not be '
                               'given the choice of adding or change their '
                               'avatars, any other value will enable avatars '
                               'for all registered users in the system')
        },
        {
            'property_name' : 'zfss_system_language',
            'property_desc' : ('System Language: This value will be used when '
                              'a user accesses the system (Anonymous User), '
                              'once the user is signed in, they will have '
                              'the opportunity of changing the language '
                              'settings for their sessions. The language '
                              'code must match any of the languages defined '
                              'in the Available Languages section.')
        },
        {
            'property_name' : 'zfss_admin_contact_email',
            'property_desc' : ('Admin Contact: (Important) - The forum '
                               'system uses this value to specify the *From* '
                               'email header for any email that is sent out, '
                               'please use a valid email address that your '
                               'domain will recognize, otherwise your '
                               'system may not send emails at all.')
        },
        {
            'property_name' : 'zfss_use_ranking_system',
            'property_desc' : ('Use Ranking System: If empty, the forum '
                               'will use default values of Member, Channel '
                               'Administrator or System Administrator, any '
                               'other value will enable forum rankings based '
                               'on the number of postings the users have '
                               '(see table member_rank for rank information.)')
        },
        {
            'property_name' : 'zfss_hot_topic_threshold',
            'property_desc' : ('Hot Topic Threshold: Number of views '
                               'necessary to mark the topic as *hot*.')
        },
        {
            'property_name' : 'zfss_member_quota',
            'property_desc' : ('Message Quota: Leave empty to disable '
                               'quotas for messages for your users, any other '
                               'numeric value will represent the number '
                               'of <b>bytes</b> of allowance, an invalid '
                               'amount will always default to 50Kb per user.')
        },
        {
            'property_name' : 'zfss_system_announcement_max',
            'property_desc' : ('System Announcements View: This controls the '
                               '(maximum) number of system announcements that '
                               'zForum will display in its right nav, an '
                               'invalid value or zero will show a =-No '
                               'System Messages-= title.')
        },
        {
            'property_name' : 'zfss_latest_postings_max',
            'property_desc' : ('Latest Postings View: This controls the '
                               '(maximum) number of latest postings that '
                               'zForum will display in its right nav, '
                               'an invalid value or zero will show '
                               'a =-No Messages-= title.')
        },
        {
            'property_name' : 'zfss_responses_per_page',
            'property_desc' : ('Responses per page: Controls the amount of '
                               'responses (children topics) that zForum '
                               'will show and will add pagination/lazy '
                               'loading accordingly.')
        },
        {
            'property_name' : 'zfss_header_html',
            'property_desc' : ('Header Text: This can contain html/markdown '
                               'code and will be shown at the top-bar of '
                               'zForum.')
        },
        {
            'property_name' : 'zfsp_available_languages',
            'property_desc' : ('Available languages to the user, use '
                               'the form: Language:languagecode_COUNTRYCODE, '
                               '(e.g. US English:en_US). Separate each '
                               'set by the PIPE Symbol (|).')
        }
    ]

    db.system_setting.bulk_insert(system_settings)

if db(db.rank).isempty():
    ranks = [
        {
            'rank_name' : 'Starfleet Ensign',
            'rank_value_min' : 0
        },
        {
            'rank_name' : 'Starfleet Lieutenant, Junior Grade',
            'rank_value_min' : 6
        },
        {
            'rank_name' : 'Starfleet Lieutenant',
            'rank_value_min' : 15
        },
        {
            'rank_name' : 'Starfleet Lieutenant Commander',
            'rank_value_min' : 40
        },
        {
            'rank_name' : 'Starfleet Commander',
            'rank_value_min' : 85
        },
        {
            'rank_name' : 'Starfleet Captain',
            'rank_value_min' : 110
        },
        {
            'rank_name' : 'Starfleet Commodore',
            'rank_value_min' : 160
        },
        {
            'rank_name' : 'Starfleet Rear Admiral',
            'rank_value_min' : 200
        },
        {
            'rank_name' : 'Starfleet Vice Admiral',
            'rank_value_min' : 250
        },
        {
            'rank_name' : 'Starfleet Admiral',
            'rank_value_min' : 500
        },
        {
            'rank_name' : 'Starfleet Fleet Admiral',
            'rank_value_min' : 1000
        }
    ]
    db.rank.bulk_insert(ranks)
