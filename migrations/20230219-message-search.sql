update comments set body=body_html where body is null and sentto is not null and parent_submission is null and length(body_html) < 10001;
