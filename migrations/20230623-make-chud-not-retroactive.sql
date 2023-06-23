alter table posts add column chudded bool default false;
alter table comments add column chudded bool default false;

alter table posts alter column chudded drop default;
alter table comments alter column chudded drop default;
