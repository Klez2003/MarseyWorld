alter table holes add column public_use bool default false not null;
alter table holes alter column public_use drop default;
