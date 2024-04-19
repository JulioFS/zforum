"""
Utilities for forum actions.
"""
import hashlib
import uuid
import os
from markdown import markdown
from py4web import URL
from .settings import Z_EXTERNAL_IMAGES, Z_INTERNAL_IMAGES
from .common import db, groups, auth

# Use imghdr (imghdr.what(fname[,stream])) to find out image type

class ForumHelper:
    """ Helper methods for different forum related actions """

    def get_system_property(self, prop, prop_default=None):
        """ retrieves a system properly value, returns property default
        if not found, if property_defult itself is not provided,
        return an empty string if none found
        """
        prop_default = '' if prop_default is None else prop_default
        db_prop = db(db.system_setting.name==prop).select(
            db.system_setting.value).first()
        return db_prop.value if db_prop is not None else prop_default

    def _generate_filename_hash(self, fname):
        """ Given a filename (fname), generate a relatively unique
        salted hash value
        """
        return hashlib.md5(
            str(uuid.uuid4()).encode('utf-8') +
            fname.encode('utf-8')).hexdigest()

    def grant_channel_admin(self, channel_id, user_id):
        """ Given a channel id and user id, upsert a record in
        channel admin table with is_active=True """
        db.channel_admin.update_or_insert(
            user_id=user_id, channel_id=channel_id, is_active=True)
        
    def revoke_channel_admin(self, channel_id, user_id):
        """ Given a channel id and user id, upsert a record in
        channel admin table with is_active=False """
        db.channel_admin.update_or_insert(
            user_id=user_id, channel_id=channel_id, is_active=False)
        
    def is_channel_admin(self, channel_id, user_id):
        """ True if user is channel admin, false otherwise """
        return db(db.channel_admin.user_id==user_id &
               db.channel_admin.channel_id==channel_id &
               db.channel_admin.is_active==True).count() > 0

    def generate_file_location(self, fname):
        """ Generates a path location where to store a file """
        hashname = self._generate_filename_hash(fname)
        return {
            'path': os.path.join(hashname[:3], hashname[3:6],
                                hashname[6:9], hashname, fname),
            'fname': fname
        }

    def verify_channel_banner(self, payload):
        """ Receives a payload (or None) and verifies it is a valid
            image to use """
        # Move to System Setings?
        available_content_types = ['image/jpeg', 'image/png']
        if payload is not None and \
            payload.content_type in available_content_types:
            # payload is in instance of
            # <ombott.request_pkg.helpers.FileUpload object at 0x107ecfc40>
            return True
        return False

    def retrieve_channel_banner(self, channel_id, banner_name):
        """ Given a channel id, retrieve the banner for it or None """
        if banner_name:
            img_path = os.path.join(
                Z_EXTERNAL_IMAGES, 'channels', str(channel_id), banner_name)
            if os.path.isfile(img_path):
                return URL(
                    'static', Z_INTERNAL_IMAGES, 'channels',
                    str(channel_id), banner_name)
        return None

    def store_channel_banner(self, channel_id, payload):
        """ receives a valid payload and creates a filesystem file """
        # <ombott.request_pkg.helpers.FileUpload object at 0x107ecfc40>
        os.makedirs(os.path.join(Z_EXTERNAL_IMAGES, 'channels',
                                 str(channel_id)), exist_ok=True)
        fn = os.path.join(Z_EXTERNAL_IMAGES, 'channels', str(channel_id),
                          payload.filename)
        payload.save(fn, overwrite=True)


    def is_sysadmin(self, user_id=None):
        """ Returns true if the user is in the Managers group,
        (See common.py for the definition of the groups table)
        """
        if user_id is None:
            # If userid is not passed, attempt to ge the current user.
            user_id = auth.get_user().get('id', None)
            if user_id is None:
                return False
        return 'manager' in groups.get(user_id)

    def is_channel_admin(self, user_id, channel_id):
        """ A channel Admin is any authenticated user that creates
        a own channel, however, a channel admin (or a sysadmin) can make
        any user administrative rights to any channel they control.
        """
        return db(
            (db.channel_admin.channel_id==channel_id) &
            (db.channel_admin.is_active==True) &
            (db.channel_admin.user_id==user_id)).count() > 0

    def get_user_properties(self, user_id=None):
        """ Returns a list of properties (ordered by Property Name)
        alongside the values belonging to the user queried, if user
        does not have the property, then it returns the set default value.
        """
        # Who is the user?
        if user_id is None:
            # If userid is not passed, attempt to ge the current user.
            user_id = auth.get_user().get('id', None)
            if user_id is None:
                return []
        # Read All available properties:
        all_user_props_r = db().select(
            db.member_setting_template.ALL,
            orderby=db.member_setting_template.name)
        # Read "used" member properties
        user_props_r = db(
            db.member_setting.user_id == user_id).select(
                db.member_setting.ALL)
        # Create our list of properties:
        # [{'Property Name': {'id': id, 'description': desc, 'value': value}}]

        # Populate a mapping of the current user's properties
        user_prop_map = {}
        if user_props_r:
            for user_prop in user_props_r:
                user_prop_map[user_prop.template_id] = user_prop.value

        # Loop thru the system properties and plug in the values of the
        # user's if applicable
        all_props = []
        for prop in all_user_props_r:
            all_props.append(
                {prop.name: {
                    'id': prop.id,
                    'description': prop.description,
                    'value': user_prop_map.get(prop.id, prop.value)}})
        return all_props

# Expose a single instance
forumhelper = ForumHelper()
