INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES
('marseyaward2','Marsey',2,'chair obama',false,1698326564),
('marseywhale','Marsey',2,'marsey fat diabetic obese mcdonalds whale fries burger soda',false,1698326462)
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
