update users set deflector=0 where deflector is null;
update users set progressivestack=0 where progressivestack is null;
update users set bird=0 where bird is null;
update users set longpost=0 where longpost is null;
update users set marseyawarded=0 where marseyawarded is null;
update users set rehab=0 where rehab is null;
update users set owoify=0 where owoify is null;
update users set bite=0 where bite is null;
update users set earlylife=0 where earlylife is null;
update users set marsify=0 where marsify is null;
update users set rainbow=0 where rainbow is null;
update users set spider=0 where spider is null;
update users set unban_utc=0 where unban_utc is null;
update users set agendaposter=0 where agendaposter is null;
update users set flairchanged=0 where flairchanged is null;
update users set patron_utc=0 where patron_utc is null;

create index users_deflector_idx on users using btree(deflector);
create index users_progressivestack_idx on users using btree(progressivestack);
create index users_bird_idx on users using btree(bird);
create index users_longpost_idx on users using btree(longpost);
create index users_marseyawarded_idx on users using btree(marseyawarded);
create index users_rehab_idx on users using btree(rehab);
create index users_owoify_idx on users using btree(owoify);
create index users_bite_idx on users using btree(bite);
create index users_earlylife_idx on users using btree(earlylife);
create index users_marsify_idx on users using btree(marsify);
create index users_rainbow_idx on users using btree(rainbow);
create index users_spider_idx on users using btree(spider);
create index users_unban_utc_idx on users using btree(unban_utc);
create index users_agendaposter_idx on users using btree(agendaposter);
create index users_flairchanged_idx on users using btree(flairchanged);
create index users_patron_utc_idx on users using btree(patron_utc);
