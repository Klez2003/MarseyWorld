alter table posts add column cw bool default false not null;

update posts set cw=true where title ilike '%[cw]%' or title ilike '%(cw)%' or title ilike '%child warning%';

alter table posts alter column cw drop default;
