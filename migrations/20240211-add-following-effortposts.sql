alter table users add column effortpost_notifs bool default false not null;
alter table users alter effortpost_notifs drop default;
