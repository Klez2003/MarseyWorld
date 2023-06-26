alter table users add column sharpen integer default 0;
alter table users alter column sharpen drop default;
CREATE INDEX users_edgified_idx ON public.users USING btree (sharpen);
