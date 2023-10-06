delete from badges where badge_id=302;
delete from badge_defs where id=302;

alter table users drop column king;
alter table posts drop column golden;
alter table comments drop column golden;
