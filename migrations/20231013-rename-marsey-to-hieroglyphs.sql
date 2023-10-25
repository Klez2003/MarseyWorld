alter table users rename column marseyawarded to hieroglyphs;
update award_relationships set kind='hieroglyphs' where kind='marsey';
