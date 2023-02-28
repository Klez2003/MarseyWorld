alter table submission_options add column body character varying(500);
update submission_options set body=body_html;
alter table submission_options alter column body set not null;

alter table comment_options add column body character varying(500);
update comment_options set body=body_html;
alter table comment_options alter column body set not null;

alter table submission_options rename column submission_id to parent_id;

alter table comment_options rename column comment_id to parent_id;
