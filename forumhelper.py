"""
Utilities for forum actions.
"""
import hashlib
import uuid
import os
from markdown import markdown
from .common import db

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


    def generate_file_location(self, fname):
        """ Generates a path location where to store a file """
        hashname = self._generate_filename_hash(fname)
        return {
            'path': os.path.join(hashname[:3], hashname[3:6],
                                hashname[6:9], hashname, fname),
            'fname': fname
        }

# Expose a single instance
forumhelper = ForumHelper()
