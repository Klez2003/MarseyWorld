create table currency_logs (
    id integer primary key,
    user_id integer not null,
    created_utc integer not null,
    currency varchar(9) not null,
    amount integer not null,
    reason varchar(1000) not null,
    balance integer not null
);

CREATE SEQUENCE public.currency_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.currency_logs_id_seq OWNED BY public.currency_logs.id;

ALTER TABLE ONLY public.currency_logs ALTER COLUMN id SET DEFAULT nextval('public.currency_logs_id_seq'::regclass);

alter table only currency_logs
    add constraint currency_logs_user_fkey foreign key (user_id) references public.users(id);

create index currency_logs_index on currency_logs using btree (user_id);
