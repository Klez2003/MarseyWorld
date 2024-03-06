create table art_submissions (
    id integer primary key,
    kind varchar(7) not null,
	author_id integer not null,
	submitter_id integer not null,
    created_utc integer not null,
	approved bool not null
);

CREATE SEQUENCE public.art_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.art_submissions_id_seq OWNED BY public.art_submissions.id;

ALTER TABLE ONLY public.art_submissions ALTER COLUMN id SET DEFAULT nextval('public.art_submissions_id_seq'::regclass);

rdrama:
    SELECT pg_catalog.setval('public.art_submissions_id_seq', 1720, true);

wpd:
    SELECT pg_catalog.setval('public.art_submissions_id_seq', 199, true);

alter table only art_submissions
    add constraint art_submissions_author_fkey foreign key (author_id) references public.users(id);

alter table only art_submissions
    add constraint art_submissions_submitter_fkey foreign key (submitter_id) references public.users(id);


delete from modactions where kind in ('approve_emoji', 'reject_emoji', 'approve_hat', 'reject_hat');
