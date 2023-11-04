#apply env vars
. /e

#generate schema.sql
pg_dump -O -x --schema-only "$DATABASE_URL" > '/d/schema.sql'

#generate seed-badges.sql
EXPORT_BADGES=$(psql --csv --tuples-only -P "null=NULL" -c \
        "SELECT ''||id||'', ' '''||name||'''', ' '''||description||'''', ' '||created_utc||'' FROM badge_defs ORDER BY id" \
        "$DATABASE_URL")
EXPORT_BADGES=$(sed 's/.*/\(&\),/' <<< "$EXPORT_BADGES")
echo "INSERT INTO public.badge_defs VALUES" > "/d/seed-badges.sql"
echo "${EXPORT_BADGES%?}" >> "/d/seed-badges.sql"
echo "ON CONFLICT (id) DO nothing;" >> "/d/seed-badges.sql"

#generate seed-hats.sql
pg_dump -O -x --data-only --inserts -t 'hat_defs' "$DATABASE_URL" > "/d/seed-hats.sql"
sed -i -E "s/(INSERT INTO public.hat_defs VALUES \(.*', )[0-9]{2,}?,/\12,/g" "/d/seed-hats.sql"
sed -i -E "s/INSERT INTO public.hat_defs VALUES \(.*, [0-9]{1,6}, [0-9]{10}\);//g" "/d/seed-hats.sql"
