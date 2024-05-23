alter table chat_memberships add column mentions int not null default 0;
alter table chat_memberships alter column mentions drop default;
