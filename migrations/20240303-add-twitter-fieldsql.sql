alter table users drop column nitter;
alter table users add column twitter varchar(50) not null default 'twitter.com';
