alter table users add column king integer;

alter table posts add column golden bool not null default false;
alter table posts alter column golden drop default;
alter table comments add column golden bool not null default false;
alter table comments alter column golden drop default;
