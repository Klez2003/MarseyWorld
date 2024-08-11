from werkzeug.security import *
from .config.const import *

def generate_hash(string):
	msg = bytes(string, "utf-16")
	return hmac.new(key=bytes(SECRET_KEY, "utf-16"),
					msg=msg,
					digestmod='md5'
					).hexdigest()


def validate_hash(string, hashstr):
	try: return hmac.compare_digest(hashstr, generate_hash(string))
	except: stop(400, "Formkey error. Please install another browser and use it make a bug report in the bug thread!")

def hash_password(password):
	return generate_password_hash(
		password, method='pbkdf2:sha512', salt_length=8)
