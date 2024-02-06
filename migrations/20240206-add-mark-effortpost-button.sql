alter table posts add column effortpost bool default false not null;
alter table posts alter column effortpost drop default;
