"""
This is an optional file that defined app level settings such as:
- database settings
- session settings
- i18n settings
This file is provided as an example:
"""
import os
from py4web.core import required_folder
from dotenv import dotenv_values

config = dotenv_values('.env')

# db settings
APP_FOLDER = os.path.dirname(__file__)
APP_NAME = os.path.split(APP_FOLDER)[-1]
# Migration files will be created below and is the store location for SQLite databases
DB_FOLDER = required_folder(APP_FOLDER, 'databases')
DB_URI = 'sqlite://storage.db'
DB_POOL_SIZE = 1
# Understanding there is a lot of confusion about Database migrations, here's
# My Take on it:
# DB_MIGRATE will create the actual SQL table unless an existing .table file
# exists, if you modify your model, and modify/add tables and whatnot, the
# best thing to do is to delete the .table file and run the app with this
# value set.
# DB_FAKE_MIGRATE seems to help in generating py4web's own metadata (.table
# files, from whatever it finds in the model, whis is very helpful.
# This is why there is usually a combination of both to make things work
# depending on your specific circumstances, but generally:
# On a brand new project, the first is True, and the Second False.
# On an existing project, where a new table is added to the model, both true.
# On an existing project, where changes are performed (add, update) to the
# model, it is best to delete the .table file(s) and set both to True
# On production, both are False.
DB_MIGRATE = config.get('DB_MIGRATE', False) # True if DB does not exist (no *.table files) (or changes to model)
DB_FAKE_MIGRATE = config.get('DB_FAKE_MIGRATE', False)  # Mainly for rebuilding metadata

# location where static files are stored:
STATIC_FOLDER = required_folder(APP_FOLDER, "static")

# send verification email on registration
VERIFY_EMAIL = True
# account requires to be approved ?
REQUIRES_APPROVAL = False
# auto login after registration
# requires False VERIFY_EMAIL & REQUIRES_APPROVAL
LOGIN_AFTER_REGISTRATION = False

# ALLOWED_ACTIONS in API / default Forms:
# ["all"]
# ["login", "logout", "request_reset_password", "reset_password", \
#  "change_password", "change_email", "profile", "config", "register",
#  "verify_email", "unsubscribe"]
# Note: if you add "login", add also "logout"
ALLOWED_ACTIONS = ["all"]

# email settings
SMTP_SSL = False
SMTP_SERVER = config.get('SMTP_SERVER', 'smtp.gmail.com:587')
SMTP_SENDER = config.get('SMTP_SENDER', 'julio@techfuel.net')
SMTP_LOGIN = config.get('SMTP_LOGIN', 'julio@techfuel.net:xxxx xxxx xxxx xxxx')
SMTP_TLS = True

# session settings
SESSION_TYPE = config.get('SESSION_TYPE', 'cookies')
SESSION_SECRET_KEY = config.get('SESSION_SECRET_KEY', 'bd962062-5840-442b-8581-756d6c738e91')
MEMCACHE_CLIENTS = ["127.0.0.1:11211"]
REDIS_SERVER = "localhost:6379"

# logger settings
LOGGERS = ["warning:stdout"]  # syntax "severity:filename" filename can be stderr or stdout

# Disable default login when using OAuth
DEFAULT_LOGIN_ENABLED = True

# Single sign on Google (will be used if provided)
OAUTH2GOOGLE_CLIENT_ID = config.get('OAUTH2GOOGLE_CLIENT_ID', None)
OAUTH2GOOGLE_CLIENT_SECRET = config.get('OAUTH2GOOGLE_CLIENT_SECRET', None)
# Single sign on Google, with stored credentials for scopes (will be used if provided).
# set it to something like os.path.join(APP_FOLDER, "private/credentials.json"
OAUTH2GOOGLE_SCOPED_CREDENTIALS_FILE = None
# single sign on Okta (will be used if provided. Please also add your tenant
# name to py4web/utils/auth_plugins/oauth2okta.py. You can replace the XXX
# instances with your tenant name.)
OAUTH2OKTA_CLIENT_ID = None
OAUTH2OKTA_CLIENT_SECRET = None
# single sign on Google (will be used if provided)
OAUTH2FACEBOOK_CLIENT_ID = None
OAUTH2FACEBOOK_CLIENT_SECRET = None
# single sign on GitHub (will be used if provided)
OAUTH2GITHUB_CLIENT_ID = None
OAUTH2GITHUB_CLIENT_SECRET = None
# i18n settings
T_FOLDER = required_folder(APP_FOLDER, "translations")
# Location of external images such as topic, posts, user images
Z_EXTERNAL_IMAGES = required_folder(APP_FOLDER, 'static', '.ext_images')
# Internal Images is a symlink to Z_EXTERNAL_IMAGES insode static so
# it can be used inside the context of http, use it like:
# URL('static', Z_INTERNAL_IMAGES, 'channels', channel_name, etc)
Z_INTERNAL_IMAGES = '.ext_images'