from files.helpers.config.const import *

def log_file(log_str, log_filename="rdrama.log"):
	'''
	Simple method to log a string to a file
	'''
	log_target = f"{LOG_DIRECTORY}/{log_filename}"
	try:
		with open(log_target, "a") as f:
			f.write(log_str + '\n')
	except Exception as e:
		print(f"Failed to log to file {log_target} due to {e.__class__.__name__}")
