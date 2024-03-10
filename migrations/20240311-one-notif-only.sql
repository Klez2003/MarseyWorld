delete from chat_notifications;

alter table chat_notifications drop column chat_message_id;

delete from chat_notifications;

alter table chat_notifications drop constraint chat_notifications_pkey;

delete from chat_notifications;

alter table chat_notifications add constraint chat_notifications_pkey primary key (user_id, chat_id);

delete from chat_notifications;
