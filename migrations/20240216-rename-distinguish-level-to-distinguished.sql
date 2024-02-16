alter table posts add column distinguished bool default false not null;
update posts set distinguished=true where distinguish_level>0;
alter table comments add column distinguished bool default false not null;
update comments set distinguished=true where distinguish_level>0;

alter table posts alter column distinguished drop default;
alter table posts drop column distinguish_level;
alter table comments alter column distinguished drop default;
alter table comments drop column distinguish_level;
