alter table users alter column custom_filter_list drop default;
update users set custom_filter_list=null where custom_filter_list = '';
update users set custom_filter_list=null where custom_filter_list = 'None';
