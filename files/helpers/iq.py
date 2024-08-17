import requests

WRITING_TO_IQ_URL = "https://www.writingtoiq.com/background_process"

def writing_to_iq(text_sample: str) -> str | None:
	"""
	Estimates the IQ of `text_sample` using `WRITING_TO_IQ_URL`.
	Returns a `str` if the request succeeds, or `None` if it fails,
	printing relevant errors to STDOUT
	"""

	try:
		res = requests.get(WRITING_TO_IQ_URL, params={"textsample": text_sample})
		res.raise_for_status()

		return res.json()["result"]
	except requests.HTTPError as ee:
		print(f"HTTP Error when requesting Writing-to-IQ: {ee}", flush=True)
		return None
	except requests.exceptions.JSONDecodeError as je:
		print(f"JSON Deoding Error when requesting Writing-to-IQ: {je}", flush=True)
		return None
