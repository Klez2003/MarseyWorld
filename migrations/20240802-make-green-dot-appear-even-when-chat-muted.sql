alter table chat_memberships add column muted bool not null default false;
alter table chat_memberships alter column muted drop default;
update chat_memberships set muted=true, notification=false where notification=null;
alter table chat_memberships alter column notification set not null;
