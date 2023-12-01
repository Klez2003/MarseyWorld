alter table users add column grinch bool default false not null;
alter table users alter column grinch drop default;
update users set grinch=true where id in (select user_id from badges where badge_id in (91,185));
update award_relationships set kind='grinch' where kind='hallowgrinch';
