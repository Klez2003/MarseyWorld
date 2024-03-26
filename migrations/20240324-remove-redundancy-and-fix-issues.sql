alter table chat_memberships add column notification bool not null default false;
alter table chat_memberships alter column notification drop default;

drop table chat_notifications;
