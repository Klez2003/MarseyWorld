. /e

#generate schema.sql
pg_dump -O -x --schema-only "$DATABASE_URL" > '/d/schema.sql'

#generate seed-badges.sql
pg_dump -O -x --data-only --inserts -t 'badge_defs' "$DATABASE_URL" > "/d/seed-badges.sql"

#generate seed-hats.sql
pg_dump -O -x --data-only --inserts -t 'hat_defs' "$DATABASE_URL" > "/d/seed-hats.sql"
sed -i -E "s/(INSERT INTO public.hat_defs VALUES \(.*', )[0-9]{2,}?,/\12,/g" "/d/seed-hats.sql"
sed -i -E "s/INSERT INTO public.hat_defs VALUES \(.*, [0-9]{1,6}, [0-9]{10}\);//g" "/d/seed-hats.sql"

#generate seed-emojis.sql
EXPORT_EMOJIS=$(psql --csv --tuples-only -P "null=NULL" -c \
        "SELECT ''''||name||'''', ''''||kind||'''', 2, ''''||tags||'''', ''''||nsfw||'''' FROM emojis WHERE submitter_id IS NULL ORDER BY name" \
        "$DATABASE_URL")
EXPORT_EMOJIS=$(sed 's/.*/\(&\),/' <<< "$EXPORT_EMOJIS")
echo "INSERT INTO public.emojis (name, kind, author_id, tags, nsfw) VALUES" > "/d/seed-emojis.sql"
echo "${EXPORT_EMOJIS%?}" >> "/d/seed-emojis.sql"
echo "ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;" >> "/d/seed-emojis.sql"
