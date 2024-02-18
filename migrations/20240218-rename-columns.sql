alter table posts rename column private to draft;

alter table posts rename column is_pinned to profile_pinned;
alter table posts rename column stickied to pinned;
alter table posts rename column stickied_utc to pinned_utc;
alter table comments rename column stickied to pinned;
alter table comments rename column stickied_utc to pinned_utc;

alter index post_is_pinned_idx rename to post_profile_pinned_idx;
alter index posts_stickied_idx rename to post_pinned_idex;
alter index post_sticked_utc_idx rename to post_pinned_utc_idex;

alter index comment_sticked_utc_idx rename to comment_pinned_utc_idex;
