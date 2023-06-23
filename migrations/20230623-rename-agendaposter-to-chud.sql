alter table users rename column agendaposter to chud;
alter table users rename column agendaposter_phrase to chud_phrase;
alter index users_agendaposter_idx rename to users_chud_idx;
update award_relationships set kind='chud' where kind='agendaposter';
