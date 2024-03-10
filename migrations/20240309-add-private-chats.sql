create table chats (
    id integer primary key,
	owner_id integer not null,
    name varchar(40) not null,
	created_utc integer not null
);

alter table chats
    add constraint chats_owner_fkey foreign key (owner_id) references users(id);

CREATE SEQUENCE public.chats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.chats_id_seq OWNED BY public.chats.id;

ALTER TABLE ONLY public.chats ALTER COLUMN id SET DEFAULT nextval('public.chats_id_seq'::regclass);


create table chat_memberships (
    user_id integer not null,
	chat_id integer not null,
	created_utc integer not null
);

alter table chat_memberships
    add constraint chat_memberships_pkey primary key (user_id, chat_id);

alter table chat_memberships
    add constraint chat_memberships_user_fkey foreign key (user_id) references users(id);

alter table chat_memberships
    add constraint chat_memberships_chat_fkey foreign key (chat_id) references chats(id);


create table chat_leaves (
    user_id integer not null,
	chat_id integer not null,
	created_utc integer not null
);

alter table chat_leaves
    add constraint chat_leaves_pkey primary key (user_id, chat_id);

alter table chat_leaves
    add constraint chat_leaves_user_fkey foreign key (user_id) references users(id);

alter table chat_leaves
    add constraint chat_leaves_chat_fkey foreign key (chat_id) references chats(id);


create table chat_messages (
    id integer primary key,
    user_id integer not null,
	chat_id integer not null,
	quotes integer,
	text varchar(1000) not null,
	text_censored varchar(1200) not null,
	text_html varchar(5000) not null,
	text_html_censored varchar(6000) not null,
	created_utc integer not null
);

alter table chat_messages
    add constraint chat_messages_user_fkey foreign key (user_id) references users(id);

alter table chat_messages
    add constraint chat_messages_chat_fkey foreign key (chat_id) references chats(id);

alter table chat_messages
    add constraint chat_messages_quotes_fkey foreign key (quotes) references chat_messages(id);


CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);

create table chat_notifications (
    user_id integer not null,
	chat_message_id integer not null,
	chat_id integer not null,
	created_utc integer not null
);

alter table chat_notifications
    add constraint chat_notifications_user_fkey foreign key (user_id) references users(id);

alter table chat_notifications
    add constraint chat_notifications_message_fkey foreign key (chat_message_id) references chat_messages(id);

alter table chat_notifications
    add constraint chat_notifications_chat_fkey foreign key (chat_id) references chats(id);

alter table chat_notifications
    add constraint chat_notifications_pkey primary key (user_id, chat_message_id);
