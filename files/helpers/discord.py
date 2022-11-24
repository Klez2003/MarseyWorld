import requests

from .const import *

def discord_message_send(channel_id, message):
	requests.post(
		f"nigger",
		headers={"nigger"},
		data={"nigger": message},
		timeout=5)

def send_changelog_message(message):
	discord_message_send(DISCORD_CHANGELOG_CHANNEL_ID, message)

def send_wpd_message(message):
	discord_message_send(WPD_CHANNEL_ID, message)
