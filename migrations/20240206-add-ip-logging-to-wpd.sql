create table ip_logs (
    user_id integer not null,
    ip varchar(39) not null,
    created_utc integer not null,
    last_used integer not null
);

alter table only ip_logs
    add constraint ip_logs_pkey primary key (user_id, ip);

alter table only ip_logs
    add constraint ip_logs_user_fkey foreign key (user_id) references public.users(id);
