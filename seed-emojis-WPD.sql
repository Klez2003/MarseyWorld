INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES
('capygun', 'Capy', 2, 'aevann mad', false, 1698332966),
('capyguts', 'Capy', 2, 'weeb anime finalfantasy', false, 1698328820),
('capyinpixel', 'Capy', 2, 'aevann sprite 8bit', false, 1698343552),
('carp6pieceeyebrowtrimmer', 'Carp', 2, 'sixpieceeyebrowtrimmer hygiene fashion', false, 1698787178),
('marsey6pieceeyebrowtrimmer', 'Marsey', 2, 'sixpieceeyebrowtrimmer hygiene fashion', false, 1698787771),
('marseyaward2', 'Marsey', 2, 'chair obama', false, 1698326564),
('marseybeingnerd', 'Marsey', 2, 'dork dweeb glasses', false, 1698330357),
('marseyconstipation', 'Marsey', 2, 'shit poop diarrhea litter constipated', false, 1698329319),
('marseydomokun', 'Marsey', 2, 'weebshit', false, 1698550172),
('marseydoodle', 'Marsey', 2, 'orangecat', false, 1698586179),
('marseyeyeball', 'Marsey', 2, 'gore bloody', false, 1698332084),
('marseygir', 'Marsey', 2, 'hottopic invaderzim', false, 1698706445),
('marseygloomybear', 'Marsey', 2, 'plushie', false, 1698638368),
('marseyinpixels', 'Marsey', 2, 'sprite 8bit', false, 1698343460),
('marseyjoyus', 'Marsey', 2, 'happy grin bucktooth yippie', false, 1698344674),
('marseymikuuu', 'Marsey', 2, 'weeb vocaloid sega', false, 1698638433),
('marseynerdy', 'Marsey', 2, 'nerd loser reading book', false, 1698342535),
('marseypinkk', 'Marsey', 2, 'pink strawberry scarf cold ill sick', false, 1698496927),
('marseytortured', 'Marsey', 2, 'slitwrists crying sad tears blood cuts tortured mutilated gore', false, 1698367179),
('marseyusatan', 'Marsey', 2, 'usagi', false, 1698470278),
('marseywhale', 'Marsey', 2, 'fat diabetic obese mcdonalds whale fries burger soda', false, 1698326462),
('marseywhat', 'Marsey', 2, 'disgust huh', false, 1698463302),
('minioncocksock', 'Misc', 2, 'cocksleeve', true, 1698334044),
('wojakselfsuck', 'Wojak', 2, 'penis cock', true, 1698333394),
('wolfamongus', 'Wolf', 2, 'sussy', false, 1698413110)
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags, kind = EXCLUDED.kind, nsfw = EXCLUDED.nsfw;
