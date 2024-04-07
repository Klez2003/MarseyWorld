alter table media add column posterurl varchar(65);
alter table media drop constraint media_pkey;
alter table media add primary key (filename);
