alter table group_memberships add column is_mod bool not null default false;
alter table group_memberships alter column is_mod drop default;
