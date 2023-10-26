INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES
('capygun', 'Capy', 2, 'aevann mad', false, 1698332966),
('capyguts', 'Capy', 2, 'weeb anime finalfantasy', false, 1698328820),
('marseyaward2', 'Marsey', 2, 'chair obama', false, 1698326564),
('marseybeingnerd', 'Marsey', 2, 'dork dweeb glasses', false, 1698330357),
('marseyconstipation', 'Marsey', 2, 'shit poop diarrhea litter constipated', false, 1698329319),
('marseyeyeball', 'Marsey', 2, 'gore bloody', false, 1698332084),
('marseynerdy', 'Marsey', 2, 'nerd marsey loser reading book', false, 1698342535),
('marseywhale', 'Marsey', 2, 'marsey fat diabetic obese mcdonalds whale fries burger soda', false, 1698326462),
('minioncocksock', 'Misc', 2, 'cocksleeve', true, 1698334044),
('wojakselfsuck', 'Wojak', 2, 'penis cock', true, 1698333394)
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
