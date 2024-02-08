alter table users add column hole_creation_notifs bool default true not null;
alter table users add column group_creation_notifs bool default false not null;
alter table users alter column hole_creation_notifs drop default;
alter table users alter column group_creation_notifs drop default;
