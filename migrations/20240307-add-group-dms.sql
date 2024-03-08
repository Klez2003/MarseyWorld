ALTER TABLE comments add COLUMN group_dm_ids int[];
update comments set group_dm_ids=ARRAY[author_id, sentto] where sentto is not null;
