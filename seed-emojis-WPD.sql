INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES
('capygun', 'Capy', 2, 'aevann mad', false, 1698332966),
('capyguts', 'Capy', 2, 'weeb anime finalfantasy', false, 1698328820),
('capyinpixel', 'Capy', 2, 'aevann sprite 8bit', false, 1698343552),
('capysudowoodo', 'Capy', 2, 'pkmn pokemon sudowoodo 185', false, 1698898310),
('carp6pieceeyebrowtrimmer', 'Carp', 2, 'sixpieceeyebrowtrimmer hygiene fashion', false, 1698787178),
('marsey6pieceeyebrowtrimmer', 'Marsey', 2, 'sixpieceeyebrowtrimmer hygiene fashion', false, 1698787771),
('marseyaward2', 'Marsey', 2, 'chair obama', false, 1698326564),
('marseybeingnerd', 'Marsey', 2, 'dork dweeb glasses', false, 1698330357),
('marseybidoof', 'Marsey', 2, 'pkmn pokemon bidoof 399', false, 1698963569),
('marseychingling', 'Marsey', 2, 'pkmn pokemon chingling 433', false, 1698905447),
('marseyconstipation', 'Marsey', 2, 'shit poop diarrhea litter constipated', false, 1698329319),
('marseydisguisedditto', 'Marsey', 2, 'pkmn pokemon ditto 132', false, 1698900406),
('marseydittoo', 'Marsey', 2, 'pkmn pokemon ditto 132', false, 1698868477),
('marseydomokun', 'Marsey', 2, 'weebshit', false, 1698550172),
('marseydoodle', 'Marsey', 2, 'orangecat', false, 1698586179),
('marseydrowzee', 'Marsey', 2, 'pkmn pokemon drowzee 096', false, 1698907206),
('marseyenderman', 'Marsey', 2, 'minecraft', false, 1698949072),
('marseyeternatus', 'Marsey', 2, 'pokemon eternatus pkmn 890', false, 1698890146),
('marseyeyeball', 'Marsey', 2, 'gore bloody', false, 1698332084),
('marseyflaaffy', 'Marsey', 2, 'pkmn pokemon flaaffy 180', false, 1698904434),
('marseyfurret', 'Marsey', 2, 'pkmn pokemon furret 162', false, 1698901966),
('marseygengar2', 'Marsey', 2, 'pkmn pokemon gengar 094', false, 1698961550),
('marseygengar8', 'Marsey', 2, 'pkmn pokemon gengar 094', false, 1698887169),
('marseygir', 'Marsey', 2, 'hottopic invaderzim', false, 1698706445),
('marseygligar', 'Marsey', 2, 'gligar pkmn pokemon 207', false, 1698907592),
('marseygloomybear', 'Marsey', 2, 'plushie', false, 1698638368),
('marseyinpixels', 'Marsey', 2, 'sprite 8bit', false, 1698343460),
('marseyjoyus', 'Marsey', 2, 'happy grin bucktooth yippie', false, 1698344674),
('marseylickitung', 'Marsey', 2, 'marsey pokemon lickitung 108', false, 1698868591),
('marseylitten', 'Marsey', 2, 'pkmn pokemon litten 725', false, 1698900234),
('marseymagmarsey', 'Marsey', 2, 'pokemon pkmn magmar 126', false, 1698870319),
('marseymango', 'Marsey', 2, 'mango marsey fruit', false, 1698874611),
('marseymikuuu', 'Marsey', 2, 'weeb vocaloid sega', false, 1698638433),
('marseymimikyu', 'Marsey', 2, 'pkmm pokemon mimikyu 778', false, 1698954421),
('marseynerdy', 'Marsey', 2, 'nerd loser reading book', false, 1698342535),
('marseyocelot', 'Marsey', 2, 'minecraft', false, 1698946895),
('marseyoshawott', 'Marsey', 2, 'pkmn pokemon oshawott 501', false, 1698896811),
('marseypalkia', 'Marsey', 2, 'marsey pkmn pokemon 484', false, 1698901055),
('marseyphanpy', 'Marsey', 2, 'pkmn pokemon phanpy 231', false, 1698906717),
('marseypinkk', 'Marsey', 2, 'pink strawberry scarf cold ill sick', false, 1698496927),
('marseyquagsire', 'Marsey', 2, 'marsey pkmn quagsire 195', false, 1698875063),
('marseyralts', 'Marsey', 2, 'pkmn pokemon ralts 280', false, 1698921737),
('marseyreshiram', 'Marsey', 2, 'pkmn pokemon reshiram 643', false, 1698901126),
('marseysableyee', 'Marsey', 2, 'pkmn pokemon sableye 302', false, 1698900966),
('marseyshiinotic', 'Marsey', 2, 'pkmn pokemon shiinotic 756', false, 1698934429),
('marseyslurpuff', 'Marsey', 2, 'pkmn pokemon slurpuff 685', false, 1698945441),
('marseystaryu', 'Marsey', 2, 'pkmn pokemon staryu 120', false, 1698882692),
('marseysylveonsit', 'Marsey', 2, 'pkmn pokemon sylveon 700', false, 1698879368),
('marseytortured', 'Marsey', 2, 'slitwrists crying sad tears blood cuts tortured mutilated gore', false, 1698367179),
('marseytoxapex', 'Marsey', 2, 'pkmn pokemon toxapex 748', false, 1698963583),
('marseyusatan', 'Marsey', 2, 'usagi', false, 1698470278),
('marseyweedle', 'Marsey', 2, 'pkmn pokemon weedle 013', false, 1698893854),
('marseywhale', 'Marsey', 2, 'fat diabetic obese mcdonalds whale fries burger soda', false, 1698326462),
('marseywhat', 'Marsey', 2, 'disgust huh', false, 1698463302),
('minioncocksock', 'Misc', 2, 'cocksleeve', true, 1698334044),
('wojakselfsuck', 'Wojak', 2, 'penis cock', true, 1698333394),
('wolfamongus', 'Wolf', 2, 'sussy', false, 1698413110)
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags, kind = EXCLUDED.kind, nsfw = EXCLUDED.nsfw;
