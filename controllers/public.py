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
from faker import Faker
import random
from pydal.validators import CRYPT


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

@action('fakepopulate')
@action.uses('pub/fakepopulate.html', db)
def fake_populate():
    # Populate the database with fake-ish data
    f = Faker()
    errors = []
    master_create = False
    create_users = True
    create_channels = True
    create_topics = True
    create_topic_responses = True
    # f.sentence(10) for 10-ish word sentences/channel title
    # f.sentence(100) for channel content
    # f.text(2000) for topic content
    # for channel tags use ''.join([l.title() for l in f.words(2)]) ==> LoveTeam, InstituteArgh, etc
    # User Creation
    # Tatiana Green/Salesforce
    if master_create:
        if create_users:
            for idx in range(100):
                password = f.password()
                crypt_password = CRYPT()(password)[0]
                payload = {
                    'username': f.user_name(),
                    'email': f.free_email(),
                    'password': crypt_password,
                    'password_again': crypt_password,
                    'first_name': f.first_name(),
                    'last_name': f.last_name()
                }
                registration_results = auth.register(payload, validate=False)
        # Grab user ids 
        user_ids = [row.id for row in db().select(db.auth_user.id)]
        if create_channels:
            for ch in range(100):
                usr_id = random.choice(user_ids)
                channel_id = db.channel.insert(
                    tag=''.join([l.title() for l in f.words(2)]),
                    title=f.sentence(10),
                    content=f.sentence(100),
                    created_by=usr_id,
                    modified_by=usr_id,
                    banner=None,
                    is_private=f.boolean(),
                    requires_membership=f.boolean())
        if create_topics:
            # creates about 50 topics per channel
            channels = db().select(db.channel.id)
            for ch in channels:
                for topic in range(50):
                    usr_id = random.choice(user_ids)
                    topic_id = db.topic.insert(
                        is_parent = True,
                        channel_id=ch.id,
                        title = f.sentence(10),
                        content = '\n'.join(f.paragraphs(10)),
                        created_by = usr_id,
                        modified_by = usr_id,
                        view=random.randint(0, 1000),
                        upvote=random.randint(0, 100)
                    )
        # grab al topic ids
        all_topics = db().select(db.topic.id, db.topic.channel_id)
        if create_topic_responses:
            # for each topic, create random(30) topic responses
            for topic in all_topics:
                num_responses = random.randint(1, 50)
                for response in range(num_responses):
                    usr_id = random.choice(user_ids)
                    topic_id = db.topic.insert(
                        is_parent = False,
                        parent_id=topic.id,
                        channel_id=topic.channel_id,
                        title = f.sentence(10),
                        content = '\n'.join(f.paragraphs(10)),
                        created_by = usr_id,
                        modified_by = usr_id,
                        view=random.randint(0, 1000),
                        upvote=random.randint(0, 100)
                    )

    return {'errors': errors}
