create function public.lifetime_donated(public.users) returns integer
    language sql immutable strict
    as $_$
      select sum(amount)
      from transactions
      where transactions.email = $1.email
      $_$;
