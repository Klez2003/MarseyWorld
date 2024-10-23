create table media_usages (
	id integer primary key,
	filename character varying(55) NOT NULL,
	post_id integer,
	comment_id integer,
	created_utc integer not null,
	deleted_utc integer,
	removed_utc integer
);

CREATE SEQUENCE public.media_usages_id_seq
	AS integer
	START WITH 1
	INCREMENT BY 1
	NO MINVALUE
	NO MAXVALUE
	CACHE 1;

ALTER TABLE ONLY public.media_usages
	ADD CONSTRAINT media_usages_unique UNIQUE NULLS NOT DISTINCT (filename, post_id, comment_id);

ALTER SEQUENCE public.media_usages_id_seq OWNED BY public.media_usages.id;

ALTER TABLE ONLY public.media_usages ALTER COLUMN id SET DEFAULT nextval('public.media_usages_id_seq'::regclass);


alter table media_usages
	add constraint media_usages_post_fkey foreign key (post_id) references posts(id);

alter table media_usages
	add constraint media_usages_comment_fkey foreign key (comment_id) references comments(id);