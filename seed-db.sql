INSERT INTO public.marseys (name, author_id, tags, created_utc) VALUES
()
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
