alter table commentflags rename to commentreports;
alter table flags rename to reports;

alter table commentreports rename constraint commentflags_pkey to commentreports_pkey;
alter table commentreports rename constraint commentflags_comment_id_fkey to commentreports_comment_id_fkey;
alter table commentreports rename constraint commentflags_user_id_fkey to commentreports_user_id_fkey;
alter table reports rename constraint flags_pkey to reports_pkey;
alter table reports rename constraint flags_post_id_fkey to reports_post_id_fkey;
alter table reports rename constraint flags_user_id_fkey to reports_user_id_fkey;

alter index cflag_user_idx rename to creport_user_idx;
alter index flag_user_idx rename to report_user_idx;
