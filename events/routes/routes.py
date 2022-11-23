from files.__main__ import *

@app.post("/trick-or-treat")
@limiter.limit("1/hour", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def trick_or_treat(v):
	if v.client: abort(403, "Not allowed from the API")

	result = random.choice([0,1])

	if result == 0:
		message = "Trick!"
	else:
		AWARDS = deepcopy(AWARDS2)
		award = random.choice(["haunt", "stab", "spiders", "fog", "flashlight", "candy-corn", "ectoplasm", "bones", "pumpkin", "jumpscare", "hw-bite", "hw-vax"])
		award_title = AWARDS[award]['title']
		award_object = AwardRelationship(user_id=v.id, kind=award)
		g.db.add(award_object)

		g.db.add(v)
		message = f"Treat! You got a {award_title} award!"
	
	return {"message": f"{message}", "result": f"{result}"}

@app.post("/jumpscare")
@auth_required
def execute_jumpscare(v):
	if v.client: abort(403, "Not allowed from the API")
	if v.jumpscare > 0:
		v.jumpscare -= 1
		g.db.add(v)
				
	return {}
