CREATE TABLE public.post_note_votes (
    note_id integer NOT NULL,
    user_id integer NOT NULL,
    vote_type integer NOT NULL,
    created_utc integer NOT NULL
);

ALTER TABLE ONLY public.post_note_votes
    ADD CONSTRAINT post_note_votes_pkey PRIMARY KEY (note_id, user_id);

ALTER TABLE ONLY public.post_note_votes
    ADD CONSTRAINT vote_note_fkey FOREIGN KEY (note_id) REFERENCES public.post_notes(id) MATCH FULL;

ALTER TABLE ONLY public.post_note_votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;

CREATE INDEX post_note_votes_vote_type_idx ON public.post_note_votes USING btree (note_id, vote_type);


CREATE TABLE public.comment_note_votes (
    note_id integer NOT NULL,
    user_id integer NOT NULL,
    vote_type integer NOT NULL,
    created_utc integer NOT NULL
);

ALTER TABLE ONLY public.comment_note_votes
    ADD CONSTRAINT comment_note_votes_pkey PRIMARY KEY (note_id, user_id);

ALTER TABLE ONLY public.comment_note_votes
    ADD CONSTRAINT vote_note_fkey FOREIGN KEY (note_id) REFERENCES public.comment_notes(id) MATCH FULL;

ALTER TABLE ONLY public.comment_note_votes
    ADD CONSTRAINT vote_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) MATCH FULL;

CREATE INDEX comment_note_votes_vote_type_idx ON public.comment_note_votes USING btree (note_id, vote_type);
