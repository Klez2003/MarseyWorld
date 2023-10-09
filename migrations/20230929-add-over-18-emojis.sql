alter table emojis add column over_18 bool default false not null;
alter table emojis alter column over_18 drop default;
