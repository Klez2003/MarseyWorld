alter table comments rename column parent_submission to parent_post;

alter index fki_save_relationship_submission_fkey rename to fki_save_relationship_post_fkey;
alter index fki_submission_sub_fkey rename to fki_post_sub_fkey;
alter index fki_submissions_approver_fkey rename to fki_post_approver_fkey;
alter index option_submission rename to option_post;

alter table award_relationships rename constraint award_submission_fkey to award_post_fkey;
alter table comments rename constraint comment_parent_submission_fkey to comment_parent_post_fkey;
alter table modactions rename constraint modactions_submission_fkey to modactions_post_fkey;
alter table post_options rename constraint option_submission_fkey to option_post_fkey;
alter table save_relationship rename constraint save_relationship_submission_fkey to save_relationship_post_fkey;
alter table subactions rename constraint subactions_submission_fkey to subactions_post_fkey;
alter table subscriptions rename constraint subscription_submission_fkey to subscription_post_fkey;
alter table post_option_votes rename constraint vote_submission_fkey to vote_post_fkey;
alter table votes rename constraint vote_submission_key to vote_post_key;
