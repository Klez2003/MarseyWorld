alter table groups add column description_html varchar(1000);
update groups set description_html=description;
