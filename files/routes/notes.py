from files.classes import *
from files.helpers.config.const import *
from files.routes.wrappers import *
from files.__main__ import app

@app.post("/vote/post/note/<int:note_id>/<vote_type>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_post_note(v, note_id, vote_type):
	vote_type = int(vote_type)

	note = g.db.get(PostNote, note_id)
	if not note: stop(404)

	existing = g.db.query(PostNoteVote).filter_by(note_id=note_id, user_id=v.id).one_or_none()
	if not existing:
		vote = PostNoteVote(
			note_id=note_id,
			user_id=v.id,
			vote_type=vote_type,
		)
		g.db.add(vote)

	return {"message": "Vote successful!"}

@app.post("/vote/comment/note/<int:note_id>/<vote_type>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_comment_note(v, note_id, vote_type):
	vote_type = int(vote_type)

	note = g.db.get(CommentNote, note_id)
	if not note: stop(404)

	existing = g.db.query(CommentNoteVote).filter_by(note_id=note_id, user_id=v.id).one_or_none()
	if not existing:
		vote = CommentNoteVote(
			note_id=note_id,
			user_id=v.id,
			vote_type=vote_type,
		)
		g.db.add(vote)

	return {"message": "Vote successful!"}