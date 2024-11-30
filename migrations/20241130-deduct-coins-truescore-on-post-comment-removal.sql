alter table posts add column coins int default 0 not null;
alter table comments add column coins int default 0 not null;
alter table posts alter column coins drop default;
alter table comments alter column coins drop default;