alter table users rename column sigs_disabled to show_sigs;
update users set show_sigs=true;
alter table users alter column show_sigs set not null;
