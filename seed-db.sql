INSERT INTO public.emojis (name, kind, author_id, tags) VALUES
()
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
