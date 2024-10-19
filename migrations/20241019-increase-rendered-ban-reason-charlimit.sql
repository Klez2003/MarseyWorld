alter table users alter column ban_reason type varchar(5000);
alter table users alter column shadowban_reason type varchar(5000);
alter table modactions alter column _note type varchar(5050);