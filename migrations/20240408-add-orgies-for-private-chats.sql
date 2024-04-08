alter table orgies add column chat_id integer not null;
alter table orgies add constraint chat_messages_chat_fkey foreign key (chat_id) references public.chats(id);
