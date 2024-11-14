create table account_deletions (
	user_id integer primary key,
	created_utc integer not null
);

alter table account_deletions
	add constraint account_deletions_user_fkey foreign key (user_id) references users(id);
