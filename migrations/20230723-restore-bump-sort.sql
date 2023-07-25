alter table posts add column bump_utc integer default 0 not null;

alter table posts alter column bump_utc drop default;

update posts set bump_utc=(SELECT CREATED_UTC FROM comments WHERE comments.created_utc is not null and parent_post = posts.id ORDER BY created_utc desc LIMIT 1) where comment_count>1;

update posts set bump_utc=created_utc where bump_utc=0;

CREATE INDEX posts_bump_utc_idx ON public.posts USING btree (bump_utc);
