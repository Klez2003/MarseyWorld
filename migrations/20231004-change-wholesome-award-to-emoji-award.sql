alter table award_relationships add column note varchar(200);

update award_relationships set kind='emoji', note='marseywholesome' where kind='wholesome';
update award_relationships set kind='emoji', note='marseypumpkin' where kind='pumpkin';
