INSERT INTO public.emojis (name, kind, author_id, tags, nsfw, created_utc) VALUES
()
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
