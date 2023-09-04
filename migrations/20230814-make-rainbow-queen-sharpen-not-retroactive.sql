alter table posts add column rainbowed bool default false not null;
alter table comments add column rainbowed bool default false not null;
alter table posts alter column rainbowed drop default;
alter table comments alter column rainbowed drop default;

alter table posts add column queened bool default false not null;
alter table comments add column queened bool default false not null;
alter table posts alter column queened drop default;
alter table comments alter column queened drop default;

alter table posts add column sharpened bool default false not null;
alter table comments add column sharpened bool default false not null;
alter table posts alter column sharpened drop default;
alter table comments alter column sharpened drop default;
