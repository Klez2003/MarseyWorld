alter table groups add column owner_id int;

alter table only groups
    add constraint groups_user_fkey foreign key (owner_id) references public.users(id);
