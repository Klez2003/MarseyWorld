UPDATE subactions SET kind = 'upload_banner' WHERE kind = 'change_banner'; -- upload_banner -> change_banner

ALTER TABLE subs RENAME COLUMN bannerurl TO bannerurls;
ALTER TABLE subs ALTER COLUMN bannerurls TYPE VARCHAR(60)[] USING ARRAY[bannerurls]; -- multiple banners <3
