update modactions set kind=replace(kind, 'marsey', 'emoji') where kind like '%marsey%';

alter table marseys rename to emojis;

alter table emojis add column kind varchar(15) not null default 'Marsey';
alter table emojis alter column kind drop default;
create index emoji_kind on public.emojis using btree (kind);
