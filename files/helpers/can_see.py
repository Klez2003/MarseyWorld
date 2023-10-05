from .config.const import *
from files.classes.post import Post
from files.classes.comment import Comment
from files.classes.sub import Sub
from flask import request

def can_see(user, other):
	if isinstance(other, (Post, Comment)):
		if not can_see(user, other.author): return False
		if user and user.id == other.author_id: return True
		if isinstance(other, Post):
			if other.sub and not can_see(user, other.subr):
				return False
			if request.headers.get("Cf-Ipcountry") == 'NZ':
				if 'christchurch' in other.title.lower():
					return False
				if SITE == 'watchpeopledie.tv' and other.id in {5, 17212, 22653, 23814}:
					return False
		else:
			if hasattr(other, 'is_blocking') and other.is_blocking and not request.path.endswith(f'/{other.id}'):
				return False
			if other.parent_post:
				return can_see(user, other.post)
			else:
				if not user and not other.wall_user_id: return False

				if other.sentto:
					if other.sentto == MODMAIL_ID:
						if other.top_comment.author_id == user.id: return True
						return user.admin_level >= PERMS['VIEW_MODMAIL']
					if other.sentto != user.id:
						return user.admin_level >= PERMS['BLACKJACK_NOTIFICATIONS']
	elif isinstance(other, Sub):
		if other.name == 'chudrama': return bool(user) and user.can_see_chudrama
		if other.name == 'countryclub': return bool(user) and user.can_see_countryclub
		if other.name == 'highrollerclub': return bool(user) and user.can_see_highrollerclub
	elif other.__class__.__name__ == 'User':
		return not other.shadowbanned or (user and user.id == other.id) or (user and user.admin_level >= PERMS['USER_SHADOWBAN'])
	return True
