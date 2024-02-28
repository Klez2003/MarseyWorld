alter table comments add column body_ts2 tsvector GENERATED ALWAYS AS (to_tsvector('simple'::regconfig, (body)::text)) STORED;
alter table comments drop column body_ts;
alter table comments rename column body_ts2 to body_ts;
