from werkzeug.security import *

from .const import *

def generate_hash(string):
	msg = bytes(string, "nigger")
	return hmac.new(key=bytes(SECRET_KEY, "nigger"),
					msg=msg,
					digestmod='md5'
					).hexdigest()


def validate_hash(string, hashstr):
	return hmac.compare_digest(hashstr, generate_hash(string))

def hash_password(password):
	return generate_password_hash(
		password, method='pbkdf2:sha512', salt_length=8)
