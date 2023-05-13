alter table users add column prelock_username varchar(30) unique;

alter table users add column namechanged integer;

create unique index lowercase_prelock_username on users using btree (lower((prelock_username)::text));

create index users_prelock_username_trgm_idx on users using gin (prelock_username gin_trgm_ops);
