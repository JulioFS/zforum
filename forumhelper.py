"""
Utilities for forum actions.
"""
import hashlib
import uuid
import os
from datetime import datetime, timedelta
from markdown import markdown
from py4web import URL
from .settings import Z_EXTERNAL_IMAGES, Z_INTERNAL_IMAGES
from .common import db, groups, auth, session

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
        """ Given a filename (fname), generate a safely unique
        salted hash value
        """
        return hashlib.md5(
            str(uuid.uuid4()).encode('utf-8') +
            fname.encode('utf-8')).hexdigest()

    def grant_channel_admin(self, channel_id, user_id):
        """ Given a channel id and user id, upsert a record in
        channel admin table with is_active=True """
        db.channel_admin.update_or_insert(
            (db.channel_admin.user_id==user_id) & \
                (db.channel_admin.channel_id==channel_id),
            user_id=user_id, channel_id=channel_id, is_active=True)
        
    def revoke_channel_admin(self, channel_id, user_id):
        """ Given a channel id and user id, upsert a record in
        channel admin table with is_active=False """
        db.channel_admin.update_or_insert(
            (db.channel_admin.user_id==user_id) & \
                (db.channel_admin.channel_id==channel_id), 
            user_id=user_id, channel_id=channel_id, is_active=False)


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
            payload.content_type.value in available_content_types:
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


    def store_topic_images(self, topic_id, payload):
        """ Retrieves a collection of images to add to a specific topic """
        # Image payload received as a collection of:
        # # <ombott.request_pkg.helpers.FileUpload object at 0x107ecfc40>
        

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
        an own channel, however, a channel admin (or a sysadmin) can make
        any user administrative rights to any channel they control.
        """
        return db(
            (db.channel_admin.channel_id==channel_id) &
            (db.channel_admin.is_active==True) &
            (db.channel_admin.user_id==user_id)).count() > 0
    
    def get_channel_membership(self, channel_id, user_id=None):
        """ Given a channel that requires membership, return True if the
        user is member of the channel, also return True if the user
        is either a System Admin, or one of the channel's administratos
        returns {'has_membership': True/False, 'is_pending': True/False}
        """
        membership_state = {
            'has_membership': False,
            'is_pending': False,
            'is_expired': False
        }
        # If user_id not passed, get it from auth
        user_id = user_id or auth.get_user().get('id', None)
        if user_id:
            # Admins and Channel Admins are _always_ members..
            if self.is_sysadmin(user_id) or \
                self.is_channel_admin(user_id, channel_id):
                membership_state['has_membership'] = True
            else:
                # Valid user, but not admin,
                # check if there is a membership record
                membership = db(
                    (db.channel_membership.user_id==user_id) &
                    (db.channel_membership.channel_id==channel_id)).select(
                        db.channel_membership.expires_on,
                        db.channel_membership.is_new_request).first()
                if membership and membership['is_new_request']:
                    membership_state['has_membership'] = True
                    membership_state['is_pending'] = True
                elif membership and (membership.expires_on >= datetime.now()):
                    membership_state['has_membership'] = True
                elif membership and (membership.expires_on < datetime.now()):
                    membership_state['is_expired'] = True
        return membership_state
    
    def grant_channel_membership(self, channel_id, user_id=None):
        """ Creates or updates a channel membership, returns True
        if success, False otherwise
        """
        granted_membership = False
        user_id = user_id or auth.get_user().get('id', None)
        if user_id:
            new_exp = datetime.now() + timedelta(years=10)
            # Update the expires on the table and use the combination of user and
            # channel for uniqueness..
            db.channel_membership.update_or_insert(
                (db.channel_membership.user_id==user_id) &
                (db.channel_membership,channel_id==channel_id),
                expires_on=new_exp)
            granted_membership = True
        return granted_membership

    def revoke_channel_membership(self, channel_id, user_id=None):
        """ Revokes a channel membership, True if success, False otherwise """
        revoked_membership = False
        user_id = user_id or auth.get_user().get('id', None)
        if user_id:
            new_exp = datetime.now() + timedelta(years=-10)
            # Update the expires on the table and use the combination of user and
            # channel for uniqueness..
            db.channel_membership.update_or_insert(
                (db.channel_membership.user_id==user_id) &
                (db.channel_membership,channel_id==channel_id),
                expires_on=new_exp)
            revoked_membership = True
        return revoked_membership
    
    def request_channel_membership(self, channel_id, user_id=None):
        """ Creates/updates a record in channel_membership que the 
        request_flag set only. To grant/revoke actual membership, 
        use the appropriate grant/revoke methods.
        """
        user_id = user_id or auth.get_user().get('id', None)
        if user_id:
            db.channel_membership.update_or_insert(
                (db.channel_membership.user_id==user_id) &
                (db.channel_membership,channel_id==channel_id),
                is_new_request=True,
                expires_on=None)

    def get_member_property(self, prop, user_id=None):
        """ Reads the member value of a property """
        if user_id is None:
            # If userid is not passed, attempt to ge the current user.
            user_id = auth.get_user().get('id', None)
            if user_id is None:
                return ''
        # get_member_property('zfmp_display_name') -> 'CapricaSOS'
        prop = db().select(
            db.member_setting_template.id,
            db.member_setting.value,
            left=db.member_setting.on(
                (db.member_setting_template.id==db.member_setting.template_id) & \
                (db.member_setting_template.name==prop) & \
                (db.member_setting.user_id==user_id)))
        prop_value = ''
        if prop:
            prop_value = prop[0].member_setting.value or ''
        return prop_value

    def put_member_properties(self, props, user_id=None):
        """ receives a list of property values and creates/updates
        the values of them.
        props = [{prop_id: 1, prop_value: 'CapricaSOS'}, ...]
        """
        if user_id is None:
            # If userid is not passed, attempt to ge the current user.
            user_id = auth.get_user().get('id', None)
            if user_id is None:
                return False
        for prop in props:
            # Use user_id and template_id to determine if record needs to be
            # inserted or updated, so if these 2 exists, then update, this
            # is done so updates to the value of a property does not trigger
            # a full insert..
            db.member_setting.update_or_insert(
                (db.member_setting.user_id==user_id) &
                (db.member_setting.template_id==prop['prop_id']),
                user_id=user_id,
                template_id=prop['prop_id'],
                value=prop['prop_value'])
        return True

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

    def get_user_info(self, user_id=None):
        """
        Compiles basic user information to be used on header/footer
        or other areas of the system, primarily information once the
        user is logged in.
        """
        session_info = {}
        if user_id is None:
            user_id = auth.get_user().get('id', None)
        if user_id:
            # Only mess with the info gathering if there is an auth user
            # Add some basic relevant user information to be available
            # on different parts of the system:
            session_info = {
                'zf_is_admin': self.is_sysadmin(user_id),
                'zf_profile_name': self.get_member_property(
                    'zfmp_display_name', user_id),
                'zf_email': auth.get_user().get('email')
            }
            session_info['zf_display_name'] = session_info[
                'zf_profile_name'] or session_info['zf_email']
        return session_info

# Expose a single instance
forumhelper = ForumHelper()
