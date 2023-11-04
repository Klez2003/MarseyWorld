alter table holes add column sidebarurls character varying(60)[] default '{}'::character varying[] not null;
update holes set sidebarurls = array_append(sidebarurls, sidebarurl) WHERE sidebarurl is not null;
alter table holes drop column sidebarurl;
