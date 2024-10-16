CREATE TABLE public.group_blacklists (
    user_id integer NOT NULL,
    group_name character varying(25) NOT NULL,
    created_utc integer NOT NULL,
    blacklister_id integer NOT NULL
);

ALTER TABLE ONLY public.group_blacklists
    ADD CONSTRAINT group_blacklists_pkey PRIMARY KEY (user_id, group_name);

ALTER TABLE ONLY public.group_blacklists
    ADD CONSTRAINT group_blacklists_group_fkey FOREIGN KEY (group_name) REFERENCES public.groups(name);

ALTER TABLE ONLY public.group_blacklists
    ADD CONSTRAINT group_blacklists_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.group_blacklists
    ADD CONSTRAINT group_blacklists_blacklister_fkey FOREIGN KEY (blacklister_id) REFERENCES public.users(id);
