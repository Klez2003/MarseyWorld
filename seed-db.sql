INSERT INTO public.users (
	username, passhash, created_utc, admin_level, over_18, is_activated, 
	original_username, defaultsorting, defaultsortingcomments, defaulttime, namecolor, titlecolor, theme, themecolor,
	cardview, reddit, pronouns, verified, profileurl, highres,
	marsify, last_viewed_post_notifs, last_viewed_log_notifs, last_viewed_reddit_notifs
) VALUES
('AutoJanny', '', extract(epoch from now()), 0, true, true, 
	'AutoJanny', 'hot', 'top', 'day', 'ff66ac', 'ff66ac', 'dark', 'ff66ac',
	false, 'old.reddit.com', 'clean/itup', 'Verified', '/i/pfps/1.webp', '/i/pfps/1.webp',
	0, 0, 0, 0),
('Snappy', '', extract(epoch from now()), 0, true, true, 
	'Snappy', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	false, 'old.reddit.com', 'beep/boop', 'Verified', '/i/pfps/2.webp', '/i/pfps/2.webp',
	0, 0, 0, 0),
('longpostbot', '', extract(epoch from now()), 0, true, true, 
	'longpostbot', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	false, 'old.reddit.com', 'tl/dr', 'Verified', '/i/pfps/3.webp', '/i/pfps/3.webp',
	0, 0, 0, 0),
('zozbot', '', extract(epoch from now()), 0, true, true, 
	'zozbot', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	false, 'old.reddit.com', 'zoz/zle', 'Verified', '/i/pfps/4.webp', '/i/pfps/4.webp',
	0, 0, 0, 0);

INSERT INTO public.marseys (name, author_id, tags, created_utc) VALUES
()
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
