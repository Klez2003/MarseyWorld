alter table users add column lifetimedonated_visible bool default false not null;
alter table users alter column lifetimedonated_visible drop default;
