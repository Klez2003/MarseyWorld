alter table subs rename to holes;

alter table subactions rename to hole_actions;
alter table hole_actions rename column sub to hole;

alter table sub_joins rename to stealth_hole_unblocks;
alter table stealth_hole_unblocks rename column sub to hole;

alter table sub_blocks rename to hole_blocks;
alter table hole_blocks rename column sub to hole;

alter table sub_subscriptions rename to hole_follows;
alter table hole_follows rename column sub to hole;

alter table mods rename column sub to hole;

alter table posts rename column sub to hole;

alter table exiles rename column sub to hole;
