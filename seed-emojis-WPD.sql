INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES
('capyguts','Capy',2,'weeb anime finalfantasy',false,1698328820),
('marseyaward2','Marsey',2,'chair obama',false,1698326564),
('marseybeingnerd','Marsey',2,'dork dweeb glasses',false,1698330357),
('marseyconstipation','Marsey',2,'shit poop diarrhea litter  constipated',false,1698329319),
('marseyeyeball','Marsey',2,'gore bloody',false,1698332084),
('marseywhale','Marsey',2,'marsey fat diabetic obese mcdonalds whale fries burger soda',false,1698326462)
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
