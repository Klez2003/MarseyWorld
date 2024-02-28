alter table users add column offsite_mentions bool;
update users set offsite_mentions=true where id in (select user_id from badges where badge_id=140);
