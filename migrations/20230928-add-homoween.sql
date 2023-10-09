alter table users add column jumpscare integer DEFAULT 0 NOT NULL;
alter table users add column zombie integer DEFAULT 0 NOT NULL;
alter table users drop column event_music;

update award_relationships set kind='bite' where kind='hw-bite';
update award_relationships set kind='vax' where kind='hw-vax';
