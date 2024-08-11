CREATE INDEX comments_body_ts_idx ON public.comments USING GIN (body_ts);
