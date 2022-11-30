import base64
import copy
import hmac
import secrets

from werkzeug.security import generate_password_hash

from files.helpers.const import (SECRET_KEY, CONTENT_SECURITY_POLICY,
                                CONTENT_SECURITY_POLICY_NONCE_LENGTH)

def generate_hash(string):
	msg = bytes(string, "utf-16")
	return hmac.new(key=bytes(SECRET_KEY, "utf-16"),
					msg=msg,
					digestmod='md5'
					).hexdigest()


def validate_hash(string, hashstr):
	return hmac.compare_digest(hashstr, generate_hash(string))

def hash_password(password):
	return generate_password_hash(
		password, method='pbkdf2:sha512', salt_length=8)

def generate_csp_nonce() -> bytes:
	'''
	Generates a nonce used for our content security policy
	'''
	return secrets.token_bytes(CONTENT_SECURITY_POLICY_NONCE_LENGTH)

def generate_csp_header(nonce:bytes) -> str:
	'''
	Generates a CSP header from a nonce that can be used in responses
	'''
	NONCE_DIRECTIVES = ["script-src", "style-src"]
	nonce_b64 = base64.b64encode(nonce) if nonce else None
	csp = copy.deepcopy(CONTENT_SECURITY_POLICY)
	to_update = {}
	if nonce_b64:
		for directive in NONCE_DIRECTIVES:
			value = csp.get(directive)
			if value: to_update[directive] = f"{value} nonce-{nonce_b64}"
	csp.update(to_update)
	return str.join(' ', [f"{directive[0]} {directive[1]};" for directive in csp.items()])
