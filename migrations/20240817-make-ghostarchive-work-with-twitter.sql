alter table users alter column twitter drop default;
update users set twitter='x.com' where twitter='twitter.com';
