alter table comments add column num_of_pinned_children int default 0 not null;
update comments set num_of_pinned_children=1 where stickied_child_id is not null;

alter table comments alter column num_of_pinned_children drop default;
alter table comments drop column stickied_child_id;
