#!/bin/bash

. /e
pg_dump -O -x --schema-only "$DATABASE_URL" > '/d/schema.sql'


OUT_FILE='/d/seed-db.sql'

rm "$OUT_FILE"

pg_dump -O -x --data-only --inserts -t 'badge_defs' "$DATABASE_URL" >> "$OUT_FILE"

pg_dump -O -x --data-only --inserts -t 'hat_defs' "$DATABASE_URL" >> "$OUT_FILE"
sed -i -E "s/(INSERT INTO public.hat_defs VALUES \(.*', )[0-9]{2,}?,/\12,/g" "$OUT_FILE"
sed -i -E "s/INSERT INTO public.hat_defs VALUES \(.*, [0-9]{1,6}, [0-9]{10}\);//g" "$OUT_FILE"


EXPORT_EMOJIS=$(psql --csv --tuples-only -P "null=NULL" -c \
        "SELECT ''''||name||'''', ''''||kind||'''', 2, ''''||tags||'''' FROM emojis WHERE submitter_id IS NULL ORDER BY name" \
        "$DATABASE_URL")
EXPORT_EMOJIS=$(sed 's/.*/\(&\),/' <<< "$EXPORT_EMOJIS")

echo "INSERT INTO public.emojis (name, kind, author_id, tags) VALUES" >> "$OUT_FILE"
echo "${EXPORT_EMOJIS%?}" >> "$OUT_FILE"
echo "ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;" >> "$OUT_FILE"

#. /scripts/g
