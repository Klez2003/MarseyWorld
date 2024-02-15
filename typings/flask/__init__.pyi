from files.classes.user import User
from flask.ctx import _AppCtxGlobals
from sqlalchemy.orm import Session
from sqlalchemy.schema import Column
import typing as t

# According to PEP 484, "all objects imported into a stub using `from ... import *` are considered
# exported", but this didn't work with Pyright for some reason, so everything has to be exported
# manually. The alternative is to put `def __getattr__(name: str) -> t.Any: ...` here instead, but
# then any symbol not in this file will be treated as Any, which prevents it from being checked.
from flask import json as json
from flask.app import Flask as Flask
from flask.blueprints import Blueprint as Blueprint
from flask.config import Config as Config
from flask.ctx import after_this_request as after_this_request
from flask.ctx import copy_current_request_context as copy_current_request_context
from flask.ctx import has_app_context as has_app_context
from flask.ctx import has_request_context as has_request_context
from flask.globals import current_app as current_app
from flask.globals import request as request
from flask.globals import session as session
from flask.helpers import abort as abort
from flask.helpers import flash as flash
from flask.helpers import get_flashed_messages as get_flashed_messages
from flask.helpers import get_template_attribute as get_template_attribute
from flask.helpers import make_response as make_response
from flask.helpers import redirect as redirect
from flask.helpers import send_file as send_file
from flask.helpers import send_from_directory as send_from_directory
from flask.helpers import stream_with_context as stream_with_context
from flask.helpers import url_for as url_for
from flask.json import jsonify as jsonify
from flask.signals import appcontext_popped as appcontext_popped
from flask.signals import appcontext_pushed as appcontext_pushed
from flask.signals import appcontext_tearing_down as appcontext_tearing_down
from flask.signals import before_render_template as before_render_template
from flask.signals import got_request_exception as got_request_exception
from flask.signals import message_flashed as message_flashed
from flask.signals import request_finished as request_finished
from flask.signals import request_started as request_started
from flask.signals import request_tearing_down as request_tearing_down
from flask.signals import template_rendered as template_rendered
from flask.templating import render_template as render_template
from flask.templating import render_template_string as render_template_string
from flask.templating import stream_template as stream_template
from flask.templating import stream_template_string as stream_template_string
from flask.wrappers import Request as Request
from flask.wrappers import Response as Response

class Globals(_AppCtxGlobals):
	agent: str
	browser: t.Literal["webview", "firefox", "iphone", "mac", "chromium"]
	db: Session
	desires_auth: bool
	is_api_or_xhr: bool
	is_tor: bool
	loggedin_chat: int
	loggedin_counter: int
	loggedout_counter: int
	nonce: str
	show_nsfw: bool
	username: Column[str]
	v: User | None

g: Globals
