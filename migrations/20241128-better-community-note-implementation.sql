alter table posts drop column community_note;
alter table comments drop column community_note;

CREATE INDEX comment_post_id_index ON public.comments USING btree (parent_post);
CREATE INDEX comment_parent_index ON public.comments USING btree (parent_comment_id);

drop INDEX post_community_notes_idx;
drop INDEX comment_community_notes_idx;

alter table award_relationships alter column note type varchar(400);




create table post_notes (
    id integer primary key,
    parent_id integer not null,
	author_id integer not null,
    body_html character varying(5000),
    created_utc integer NOT NULL
);

CREATE SEQUENCE public.post_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.post_notes_id_seq OWNED BY public.post_notes.id;

ALTER TABLE ONLY public.post_notes ALTER COLUMN id SET DEFAULT nextval('public.post_notes_id_seq'::regclass);

alter table only post_notes
    add constraint post_notes_post_fkey foreign key (parent_id) references public.posts(id);

alter table only post_notes
    add constraint post_notes_author_fkey foreign key (author_id) references public.users(id);

CREATE INDEX note_post_idx ON public.post_notes USING btree (parent_id);



create table comment_notes (
    id integer primary key,
    parent_id integer not null,
	author_id integer not null,
    body_html character varying(5000),
    created_utc integer NOT NULL
);

CREATE SEQUENCE public.comment_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.comment_notes_id_seq OWNED BY public.comment_notes.id;

ALTER TABLE ONLY public.comment_notes ALTER COLUMN id SET DEFAULT nextval('public.comment_notes_id_seq'::regclass);

alter table only comment_notes
    add constraint comment_notes_comment_fkey foreign key (parent_id) references public.comments(id);

alter table only comment_notes
    add constraint comment_notes_author_fkey foreign key (author_id) references public.users(id);

CREATE INDEX note_comment_idx ON public.comment_notes USING btree (parent_id);