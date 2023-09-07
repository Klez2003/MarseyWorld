INSERT INTO public.users (
	username, passhash, created_utc, admin_level, email_verified,
	original_username, defaultsorting, defaultsortingcomments, defaulttime, namecolor, titlecolor, theme, themecolor,
	reddit, pronouns, verified, profileurl, highres,
	marsify, last_viewed_post_notifs, last_viewed_log_notifs, last_viewed_reddit_notifs, lifetimedonated, lifetimedonated_visible
) VALUES
('AutoJanny', '', extract(epoch from now()), 0, true,
	'AutoJanny', 'hot', 'top', 'day', 'ff459a', 'ff459a', 'dark', 'ff459a',
	'old.reddit.com', 'clean/itup', 'Verified', '/i/pfps/1.webp', '/i/pfps/1.webp',
	0, 0, 0, 0, 0, false),
('Snappy', '', extract(epoch from now()), 0, true,
	'Snappy', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	'old.reddit.com', 'beep/boop', 'Verified', '/i/pfps/2.webp', '/i/pfps/2.webp',
	0, 0, 0, 0, 0, false),
('longpostbot', '', extract(epoch from now()), 0, true,
	'longpostbot', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	'old.reddit.com', 'tl/dr', 'Verified', '/i/pfps/3.webp', '/i/pfps/3.webp',
	0, 0, 0, 0, 0, false),
('zozbot', '', extract(epoch from now()), 0, true,
	'zozbot', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	'old.reddit.com', 'zoz/zle', 'Verified', '/i/pfps/4.webp', '/i/pfps/4.webp',
	0, 0, 0, 0, 0, false);
