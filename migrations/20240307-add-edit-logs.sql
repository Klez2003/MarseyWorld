create table post_edits (
    id integer primary key,
    post_id integer not null,
    old_title character varying(500),
    old_title_html character varying(1500),
    old_body character varying(100000),
    old_body_html character varying(200000),
    created_utc integer NOT NULL
);

CREATE SEQUENCE public.post_edits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.post_edits_id_seq OWNED BY public.post_edits.id;

ALTER TABLE ONLY public.post_edits ALTER COLUMN id SET DEFAULT nextval('public.post_edits_id_seq'::regclass);

alter table only post_edits
    add constraint post_edits_post_fkey foreign key (post_id) references public.posts(id);


create table comment_edits (
    id integer primary key,
    comment_id integer not null,
    old_body character varying(100000),
    old_body_html character varying(200000),
    created_utc integer NOT NULL
);

CREATE SEQUENCE public.comment_edits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.comment_edits_id_seq OWNED BY public.comment_edits.id;

ALTER TABLE ONLY public.comment_edits ALTER COLUMN id SET DEFAULT nextval('public.comment_edits_id_seq'::regclass);

alter table only comment_edits
    add constraint comment_edits_comment_fkey foreign key (comment_id) references public.comments(id);
