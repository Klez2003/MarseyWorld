alter table comments drop column body_ts;
alter table comments add column body_ts tsvector GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, (body)::text)) STORED;
