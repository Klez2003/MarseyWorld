create table groups (
    name character varying(25) primary key,
    created_utc integer not null
);

create index groups_index on groups using btree (created_utc asc);

create table group_memberships (
    user_id integer not null,
    group_name varchar(25) not null,
    created_utc integer not null,
	approved_utc integer
);

alter table only group_memberships
    add constraint group_memberships_pkey primary key (user_id, group_name);

alter table only group_memberships
    add constraint group_memberships_user_fkey foreign key (user_id) references public.users(id);

alter table only group_memberships
    add constraint group_memberships_group_fkey foreign key (group_name) references public.groups(name);
