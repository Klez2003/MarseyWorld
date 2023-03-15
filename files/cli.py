import os
from pathlib import Path

# cli.py runs in <repo-root>/files, whereas our relative paths assume
# the WD is <repo-root>. NOTE: Change this if cli.py is ever moved.
os.chdir(Path(__file__).parent.parent)

from .__main__ import app, cache
from flask import g
import files.helpers.cron
