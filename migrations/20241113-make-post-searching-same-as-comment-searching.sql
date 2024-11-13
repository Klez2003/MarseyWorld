alter table posts add column title_ts tsvector GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, (title)::text)) STORED;
alter table posts add column body_ts tsvector GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, (body)::text)) STORED;
alter table posts add column url_ts tsvector GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, (url)::text)) STORED;
alter table posts add column embed_ts tsvector GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, (embed)::text)) STORED;

CREATE INDEX posts_title_ts_idx ON public.posts USING gin (title_ts);
CREATE INDEX posts_body_ts_idx ON public.posts USING gin (body_ts);
CREATE INDEX posts_url_ts_idx ON public.posts USING gin (url_ts);
CREATE INDEX posts_embed_ts_idx ON public.posts USING gin (embed_ts);