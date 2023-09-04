update posts set ping_cost=0 where ping_cost is null;
alter table posts alter column ping_cost set not null;
update comments set ping_cost=0 where ping_cost is null;
alter table comments alter column ping_cost set not null;
