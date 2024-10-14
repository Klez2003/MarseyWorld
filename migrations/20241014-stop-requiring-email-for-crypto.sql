alter table transactions alter column email drop not null;

alter table transactions add column user_id int;

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

CREATE INDEX transactions_user_idx ON public.transactions USING btree (user_id);
