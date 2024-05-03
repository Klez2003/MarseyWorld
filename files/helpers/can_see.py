from .config.const import *
from files.classes.post import Post
from files.classes.comment import Comment
from files.classes.hole import Hole
from flask import request

#DELETE_ME_PLS
words_to_hide = ('israel', 'isreal', 'palest', 'muslim', 'islam', 'hamas', 'jew', 'zion', 'gaza', 'rafah', 'isis', 'terror', 'iraq', 'allah', 'mohammad', 'muhammad', 'mohammed', 'muhammed', 'mohamad', 'muhamad', 'mohamed', 'muhamed', 'trans', 'train', 'tranny', 'troon', 'rowdy', 'nigger', 'bipoc')

def can_see(user, obj):
	if isinstance(obj, (Post, Comment)):
		#DELETE_ME_PLS
		if not user:
			if obj.nsfw:
				return False
			if any((x in obj.body.lower() for x in words_to_hide)):
				return False

		if not can_see(user, obj.author): return False
		if user and user.id == obj.author_id: return True
		if isinstance(obj, Post):
			if obj.hole and not can_see(user, obj.hole_obj):
				return False
			if request.headers.get("Cf-Ipcountry") == 'NZ':
				if 'christchurch' in obj.title.lower():
					return False
				if SITE == 'watchpeopledie.tv' and obj.id in {5, 17212, 22653, 23814}:
					return False
		else:
			if obj.pinned == "Admin Note":
				return user and user.admin_level >= PERMS['ADMIN_NOTES']
			if hasattr(obj, 'is_blocking') and obj.is_blocking and not request.path.endswith(f'/{obj.id}'):
				return False
			if obj.parent_post:
				return can_see(user, obj.post)
			else:
				if not user and not obj.wall_user_id: return False

				if obj.sentto:
					if obj.sentto == MODMAIL_ID:
						if obj.top_comment.author_id == user.id: return True
						return user.admin_level >= PERMS['VIEW_MODMAIL']
					if obj.sentto != user.id:
						return user.admin_level >= PERMS['BLACKJACK_NOTIFICATIONS']
	elif isinstance(obj, Hole):
		if obj.name == 'chudrama': return bool(user) and user.can_see_chudrama
		if obj.name == 'countryclub': return bool(user) and user.can_see_countryclub
		if obj.name == 'highrollerclub': return bool(user) and user.can_see_highrollerclub
		#DELETE_ME_PLS
		if obj.name in {'sandshit', 'isis', 'facism', 'furry', 'fatpeoplehate', 'toomanyxchromosomes', 'drugs', 'faggot', 'spalspace', 'deadniggerstorage'}: return bool(user)
	elif obj.__class__.__name__ == 'User':
		#DELETE_ME_PLS
		if obj.id == 21238: return False
		return not obj.shadowbanned or (user and user.id == obj.id) or (user and user.admin_level >= PERMS['USER_SHADOWBAN'])
	return True
