alter table users add column hide_cw bool default false not null;
alter table users alter column hide_cw drop default;
