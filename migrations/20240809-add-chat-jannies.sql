alter table chat_memberships add column is_mod bool not null default false;
alter table chat_memberships alter column is_mod drop default;

DO
$do$
BEGIN 
	FOR i IN 1..600 LOOP
		update chat_memberships m1 set is_mod=true where chat_id = i and user_id = (select user_id from chat_memberships m2 where m1.chat_id = m2.chat_id order by created_utc limit 1);
	END LOOP;
END
$do$;
