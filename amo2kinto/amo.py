import hashlib
import uuid


def make_id_from_string(string):
    hashed = hashlib.md5(string.encode('utf-8'))
    return str(uuid.UUID(hashed.hexdigest()))
