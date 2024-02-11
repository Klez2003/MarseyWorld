alter table users add column shadowban_reason varchar(256);
update users set shadowban_reason=ban_reason where shadowbanned is not null;
update users set ban_reason=null where is_banned is null and ban_reason is not null;
