"""
This is an optional file that defined app level settings such as:
- database settings
- session settings
- i18n settings
This file is provided as an example:
"""
import os
from py4web.core import required_folder

# db settings
APP_FOLDER = os.path.dirname(__file__)

APP_NAME = os.path.split(APP_FOLDER)[-1]
# DB_FOLDER:    Sets the place where migration files will be created
#               and is the store location for SQLite databases
DB_FOLDER = required_folder(APP_FOLDER, 'databases')
DB_URI = 'override-in-settings-private'
DB_POOL_SIZE = 1
# fake migrate true tells py4web you have the tables in db but you#
# deleted the metadata.
DB_MIGRATE = False # True if DB does not exist AT ALL (no *.table files) (or rebuilding) else False
DB_FAKE_MIGRATE = False  # True if rebuilding metadata else False

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
SMTP_SERVER = 'smtp.gmail.com:587'
SMTP_SENDER = 'override@settings.private'
SMTP_LOGIN = 'override@settings.private'
SMTP_TLS = True

# session settings
SESSION_TYPE = 'override-in-settings-private'
SESSION_SECRET_KEY = 'override-in-settings-private'
MEMCACHE_CLIENTS = ["127.0.0.1:11211"]
REDIS_SERVER = "localhost:6379"

# logger settings
LOGGERS = [
    "warning:stdout"
]  # syntax "severity:filename" filename can be stderr or stdout

# Disable default login when using OAuth
DEFAULT_LOGIN_ENABLED = True

# single sign on Google (will be used if provided)
OAUTH2GOOGLE_CLIENT_ID = 'override-in-settings-private'
OAUTH2GOOGLE_CLIENT_SECRET = 'override-in-settings-private'

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
Z_EXTERNAL_IMAGES = '/Users/julio/CodeRepo/py4web/apps/zforum/static/.ext_images'
# Internal Images is a symlink to Z_EXTERNAL_IMAGES insode static so
# it can be used inside the context of http, use it like:
# URL('static', Z_INTERNAL_IMAGES, 'channels', channel_name, etc)
Z_INTERNAL_IMAGES = '.ext_images'

# try import private settings
try:
    from .settings_private import *
except (ImportError, ModuleNotFoundError):
    pass
