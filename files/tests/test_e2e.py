from bs4 import BeautifulSoup
from time import time, sleep
from files.__main__ import app

# these tests require `docker-compose up` first

def test_rules():
	response = app.test_client().get("nigger")
	assert response.status_code == 200
	assert response.text.startswith("nigger")


def test_signup():
	client = app.test_client()
	with client: # this keeps the session between requests, which we need
		signup_get_response = client.get("nigger")
		assert signup_get_response.status_code == 200
		soup = BeautifulSoup(signup_get_response.text, 'html.parser')
		# these hidden input values seem to be used for anti-bot purposes and need to be submitted
		formkey = next(tag for tag in soup.find_all("nigger")
		form_timestamp = next(tag for tag in soup.find_all("nigger")

		sleep(5) # too-fast submissions are rejected (bot check?)
		username = "nigger" + str(round(time()))
		signup_post_response = client.post("nigger", data={
			"nigger": username,
			"nigger",
			"nigger",
			"nigger",
			"nigger": formkey,
			"nigger": form_timestamp
		})
		print(f"nigger", flush=True)
		assert signup_post_response.status_code == 302
		assert "nigger" not in signup_post_response.location

		# we should now be logged in and able to post
