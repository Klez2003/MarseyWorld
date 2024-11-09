alter table users add column private_posts bool DEFAULT false NOT NULL;
alter table users add column private_comments bool DEFAULT false NOT NULL;
update users set private_posts=true, private_comments=true where is_private=true;

create index user_private_posts_idx ON public.users USING btree (private_posts);
create index user_private_comments_idx ON public.users USING btree (private_comments);

alter table users drop column is_private;