update badge_defs set name='X', description='X' where id=21;
update badge_defs set name='Paypig', description='Contributes $5/month' where id=22;
update badge_defs set name='Renthog', description='Contributes $10/month' where id=23;
update badge_defs set name='Landchad', description='Contributes $20/month' where id=24;
update badge_defs set name='Terminally online turboautist', description='Contributes $50/month' where id=25;
update badge_defs set name='Marsey''s Sugar Daddy', description='Contributes $100/month' where id=26;
update badge_defs set name='JIDF Bankroller', description='Contributes $200/month' where id=27;
update badge_defs set name='Rich Bich', description='Contributes $500/month' where id=28;

INSERT INTO public.badge_defs VALUES (58, 'Chud', 'Marked as a chud', NULL);
update badges set badge_id=58 where badge_id=28;

update badges set badge_id=badge_id+1 where badge_id in (21,22,23,24,25,26,27);
delete from badge_defs where id=21;

update users set patron=1 where patron>0;
update users set patron=2 where id in (select user_id from badges where badge_id=22);
update users set patron=3 where id in (select user_id from badges where badge_id=23);
update users set patron=4 where id in (select user_id from badges where badge_id=24);
update users set patron=5 where id in (select user_id from badges where badge_id=25);
update users set patron=6 where id in (select user_id from badges where badge_id=26);
update users set patron=7 where id in (select user_id from badges where badge_id=27);
update users set patron=8 where id in (select user_id from badges where badge_id=28);

update users set patron=0 where patron>0 and patron_utc=0;
