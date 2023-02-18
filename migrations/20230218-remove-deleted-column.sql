delete from alts where deleted=true;
alter table alts drop column deleted;
