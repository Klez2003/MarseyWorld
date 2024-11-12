from files.helpers.regex import *
import re

def sharpen(string, chud_phrase):
	if chud_phrase:
		string = re.sub(chud_phrase, 'erfdsx34224e4535resfed', string, flags=re.I)

	string = the_fucking_regex.sub("\g<1><2> fucking", string)
	string = bitch_question_mark_regex.sub(", bitch?", string)
	string = exclamation_point_regex.sub(", motherfucker!", string)

	if chud_phrase:
		string = string.replace('erfdsx34224e4535resfed', chud_phrase)

	return string
