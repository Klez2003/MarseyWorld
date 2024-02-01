alter table users add column last_viewed_modmail_notifs int not null default 0;
alter table users alter column last_viewed_modmail_notifs drop default;
