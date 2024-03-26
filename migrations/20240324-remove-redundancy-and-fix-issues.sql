alter table chat_memberships add column notification bool not null default false;
alter table chat_memberships alter column notification drop default;

alter table chat_memberships add column last_notified int;
update chat_memberships a set last_notified=(select created_utc from chat_messages b where a.chat_id=b.chat_id order by created_utc desc limit 1);
update chat_memberships set last_notified=0 where last_notified is null;
alter table chat_memberships alter column last_notified set not null;

drop table chat_notifications;
