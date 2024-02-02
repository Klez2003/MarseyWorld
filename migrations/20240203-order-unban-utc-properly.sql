alter table users alter column unban_utc drop not null;
update users set unban_utc=null where unban_utc=0;
