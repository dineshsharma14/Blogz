import hashlib
import string, random

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for i in range(5)])

def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password)).hexdigest()    
    return '{0},{1}'.format(hash, salt)

def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
    
    return False