from files.helpers.regex import *

def sharpen(string, v):
	if v.chud_phrase:
		string = string.replace(v.chud_phrase, 'erfdsx34224e4535resfed')

	string = the_fucking_regex.sub("\g<1> fucking", string)
	string = bitch_question_mark_regex.sub(", bitch?", string)
	string = exclamation_point_regex.sub(", motherfucker!", string)

	if v.chud_phrase:
		string = string.replace('erfdsx34224e4535resfed', v.chud_phrase)

	return string
