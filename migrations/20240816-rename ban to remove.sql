update modactions set kind='remove_comment' where kind='ban_comment';
update modactions set kind='approve_comment' where kind='unban_comment';
update modactions set kind='remove_post' where kind='ban_post';
update modactions set kind='approve_post' where kind='unban_post';
