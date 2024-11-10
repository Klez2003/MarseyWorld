from .config.const import *
from files.classes.post import Post
from files.classes.comment import Comment
from files.classes.hole import Hole
from flask import request

def can_see(user, obj):
	if isinstance(obj, (Post, Comment)):
		if not can_see(user, obj.author): return False
		if user and user.id == obj.author_id: return True
		if isinstance(obj, Post):
			if obj.hole and not can_see(user, obj.hole_obj):
				return False
			if request.headers.get("Cf-Ipcountry") == 'NZ':
				if 'christchurch' in obj.title.lower():
					return False
				if SITE == 'watchpeopledie.tv' and obj.id in {5, 17212, 22653, 23814, 222321}:
					return False
		else:
			if obj.pinned == "Admin Note":
				return user and user.admin_level >= PERMS['ADMIN_NOTES']
			if hasattr(obj, 'is_blocking') and obj.is_blocking and not request.path.endswith(f'/{obj.id}'):
				return False
			if obj.parent_post:
				if request.path == '/comments' and obj.post.draft:
					return False
				return can_see(user, obj.post)
			else:
				if not user and not obj.wall_user_id: return False

				if obj.sentto:
					if obj.sentto == MODMAIL_ID:
						if obj.top_comment.author_id == user.id: return True
						return user.admin_level >= PERMS['VIEW_MODMAIL']
					if obj.sentto != user.id:
						return user.admin_level >= PERMS['VIEW_CHATS']
	elif isinstance(obj, Hole):
		if obj.name == 'chudrama': return bool(user) and user.can_see_chudrama
		if obj.name == 'countryclub': return bool(user) and user.can_see_countryclub
		if obj.name == 'highrollerclub': return bool(user) and user.can_see_highrollerclub
	elif obj.__class__.__name__ == 'User':
		if obj.id == CROSSTALK_ID:
			return user and user.can_see_countryclub
		return not obj.shadowbanned or (user and user.id == obj.id) or (user and user.admin_level >= PERMS['USER_SHADOWBAN'])
	return True
