alter table users rename column coins_spent to currency_spent_on_awards;
alter table users rename column coins_spent_on_hats to currency_spent_on_hats;

drop index users_coins_spent_on_hats_idx;
create index users_currency_spent_on_awards_idx ON public.users USING btree (currency_spent_on_awards desc);

update badge_defs set description='Spent 10,000 currency on awards' where id=69;
update badge_defs set description='Spent 100,000 currency on awards' where id=70;
update badge_defs set description='Spent 250,000 currency on awards' where id=71;
update badge_defs set description='Spent 500,000 currency on awards' where id=72;
update badge_defs set description='Spent a fucking million currency on awards' where id=73;
