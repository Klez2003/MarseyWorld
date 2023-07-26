cd /db
. /e
pg_dump -O -Fc "$DATABASE_URL" > `date +%d-%H`.pgsql
