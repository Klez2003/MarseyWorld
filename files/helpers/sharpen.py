import re
from files.helpers.regex import *

def sharpen(string):
    string = the_fucking_regex.sub("\g<1> fucking", string)
    string = bitch_question_mark_regex.sub(", bitch?", string)
    string = exclamation_point_regex.sub(", motherfucker!", string)
    return string
