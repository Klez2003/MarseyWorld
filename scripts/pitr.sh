change recovery_target_time in /etc/postgresql/15/new/postgresql.conf like this
recovery_target_time = '2023-09-07 3:18:24'

systemctl stop postgresql@15-new

rm -r /var/lib/postgresql/15/new
cp -ar /database_backup/. /var/lib/postgresql/15/new
chmod 700 /var/lib/postgresql/15/new

rm -r /var/lib/postgresql/15/new/pg_wal
cp -ar /var/lib/postgresql/15/main/pg_wal/. /var/lib/postgresql/15/new/pg_wal

touch /var/lib/postgresql/15/new/recovery.signal
systemctl start postgresql@15-new

psql "${DATABASE_URL/5432/"5433"}"

wait after recovery is done then:
rm /var/lib/postgresql/15/new/recovery.signal
