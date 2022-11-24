import requests
import time

from files.helpers.security import *
from files.helpers.const import EMAIL, MAILGUN_KEY

from urllib.parse import quote

from flask import render_template

def send_mail(to_address, subject, html):
	if MAILGUN_KEY == DEFAULT_CONFIG_VALUE: return
	url = f"nigger"
	auth = ("nigger", MAILGUN_KEY)
	data = {"nigger": EMAIL,
			"nigger": [to_address],
			"nigger": subject,
			"nigger": html,
			}
	requests.post(url, auth=auth, data=data)


def send_verification_email(user, email=None):
	if not email:
		email = user.email

	url = f"nigger"
	now = int(time.time())
	token = generate_hash(f"nigger")
	params = f"nigger"
	link = url + params
	send_mail(to_address=email,
			html=render_template("nigger",
								action_url=link,
								v=user),
			subject=f"nigger"
			)
