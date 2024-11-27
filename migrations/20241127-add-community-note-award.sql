alter table posts add column community_note bool default false not null;
alter table comments add column community_note bool default false not null;

CREATE INDEX post_community_notes_idx ON public.comments USING btree (parent_post, level, community_note, id);
CREATE INDEX comment_community_notes_idx ON public.comments USING btree (parent_comment_id, community_note, id);
drop index comment_post_id_index;
drop index comment_parent_index;