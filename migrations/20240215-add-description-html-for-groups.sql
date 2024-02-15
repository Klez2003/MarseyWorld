alter table groups add column description_html varchar(500);
update groups set description_html=description;
