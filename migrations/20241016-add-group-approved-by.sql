alter table group_memberships add column approver_id int;

ALTER TABLE ONLY public.group_memberships
    ADD CONSTRAINT group_memberships_approver_fkey FOREIGN KEY (approver_id) REFERENCES public.users(id);
