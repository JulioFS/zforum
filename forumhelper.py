"""
Utilities for forum actions.
"""
import hashlib
import uuid
import os

# Use imghdr (imghdr.what(fname[,stream])) to find out image type

def _generate_filename_hash(fname):
    """ Given a filename (fname), generate a relatively unique
    salted hash value
    """
    return hashlib.md5(
        str(uuid.uuid4()).encode('utf-8') + fname.encode('utf-8')).hexdigest()


def getnerate_file_location(fname):
    """ Generates a path location where to store a file """
    hashname = _generate_filename_hash(fname)
    return {
        'path': os.path.join(hashname[:3], hashname[3:6],
                             hashname[6:9], hashname, fname),
        'fname': fname
    }
