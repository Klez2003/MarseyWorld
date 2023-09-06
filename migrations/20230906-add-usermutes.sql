CREATE TABLE public.usermutes (
    user_id integer NOT NULL,
    target_id integer NOT NULL,
    created_utc integer
);

ALTER TABLE ONLY public.usermutes
    ADD CONSTRAINT usermutes_pkey PRIMARY KEY (user_id, target_id);


CREATE INDEX mute_target_idx ON public.usermutes USING btree (target_id);

ALTER TABLE ONLY public.usermutes
    ADD CONSTRAINT mute_target_fkey FOREIGN KEY (target_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.usermutes
    ADD CONSTRAINT mute_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
