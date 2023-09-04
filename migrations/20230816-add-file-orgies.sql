drop table public.orgies;
CREATE TABLE public.orgies (
    type character varying(8) primary key,
    data character varying(200) NOT NULL,
    title character varying(1000) NOT NULL,
	created_utc int not null
);
