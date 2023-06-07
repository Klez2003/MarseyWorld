alter table submissions rename to posts;
alter table submission_options rename to post_options;
alter table submission_option_votes rename to post_option_votes;

alter table award_relationships rename column submission_id to post_id;
alter table save_relationship rename column submission_id to post_id;
alter table post_option_votes rename column submission_id to post_id;
alter table subscriptions rename column submission_id to post_id;
alter table votes rename column submission_id to post_id;

alter table modactions rename column target_submission_id to target_post_id;
alter table subactions rename column target_submission_id to target_post_id;
