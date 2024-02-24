"""
ZForum database model.
"""

import datetime
#from pydal.validators import *
from .common import db, Field

now = datetime.datetime.utcnow

db.define_table(
    'channel',
    Field('tag'), # Must Index
    Field('title', required=True),
    Field('content', type='text'), # Use for some blob, optional.
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
    Field('is_active', type='Boolean', default=True)
)
db.commit()

# This table contains both topic and responses, with is_parent properly
# identifying the topic as "parent", and parent_id (being not null)
# identifying (a) being a child, and (b) of which main topic
db.define_table(
    'topic',
    Field('channel_id', 'reference channel'),
    # Title is not required for topic responses, enforce in code/UI
    Field('title'),
    Field('content', required=True),
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
    Field('name'),
    Field('display_order', type='number')
)
db.commit()

db.define_table(
    'message',
    Field('category_id', 'reference message_categories'),
    Field('is_read', type='boolean', default=False),
    Field('user_id', 'reference auth_user'),
    Field('from_user_id', 'reference auth_user'),
    Field('subject', required=True),
    Field('message', type='text', required=True),
    Field('created_on', type='datetime', default=now)
)
db.commit()

# E.g. ['initial_message': 'Welcome {user} to the new system']
db.define_table(
    'system_message_template',
    Field('key', required=True),
    Field('content', required=True)
)
db.commit()

# E.g. ['threads_per_page', '100', 'Number of topics per page'],
# ['use_rank_system', 'False', 'Use Rank System']
db.define_table(
    'system_setting',
    Field('name', required=True),
    Field('value'),
    Field('description')
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
    Field('topic_id'),
    Field('is_active', type='boolean', default=True)
)
db.commit()

db.define_table(
    'rank',
    Field('Name'),
    Field('min_value', type='integer', notnull=True)
)
db.commit()

# ['user_fullname', 'User Full Name:', True],
# ['last_login', 'Last Login:', False]
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
    Field('value')
)
db.commit()

db.define_table(
    'member_avatar',
    Field('user_id', 'reference auth_user'),
    Field('avatar', type='text'),
    Field('content_type')
)
db.commit()

db.define_table(
    'available_languages',
    Field('code', notnull=True), # 'en/us'
    Field('description', notnull=True) # 'English (US)'
)
db.commit()

# Images will be stored in the filesystem, a hash will be
# created to identity the location of the files (https://techfuel.net/story/3)
db.define_table(
    'topic_image',
    Field('topic_id', 'reference topic'),
    Field('image_hash', notnull=True)
)
db.commit()
