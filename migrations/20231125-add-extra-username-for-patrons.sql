alter table users add column extra_username character varying(30) unique;

CREATE UNIQUE INDEX lowercase_extra_username ON public.users USING btree (lower((extra_username)::text));

CREATE INDEX users_extra_username_trgm_idx ON public.users USING gin (extra_username public.gin_trgm_ops);
