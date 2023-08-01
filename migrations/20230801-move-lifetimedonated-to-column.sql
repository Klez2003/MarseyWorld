alter table users add column lifetimedonated int not null default 0;
alter table users alter column lifetimedonated drop default;
update users set lifetimedonated=(select sum(amount) from transactions where transactions.email = users.email) where (select sum(amount) from transactions where transactions.email = users.email)>0;
