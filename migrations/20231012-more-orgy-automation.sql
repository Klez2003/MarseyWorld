alter table orgies add column start_utc int not null;
alter table orgies add column started bool not null;
update modactions set kind='schedule_orgy' where kind='start_orgy';
update modactions set kind='remove_orgy' where kind='stop_orgy';
ALTER TABLE orgies DROP CONSTRAINT orgies_pkey;
ALTER TABLE orgies ADD PRIMARY KEY (created_utc);
