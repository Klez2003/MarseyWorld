systemctl stop postgresql@15-main
mv /var/lib/postgresql/15/main/pg_wal /pg_wal
rm -rf /var/lib/postgresql/15/main
mkdir /var/lib/postgresql/15/main
cp -a /database_backup/. /var/lib/postgresql/15/main
chown postgres:postgres /var/lib/postgresql/15/main
chmod 700 /var/lib/postgresql/15/main
rm -rf /var/lib/postgresql/15/main/pg_wal
mv /pg_wal /var/lib/postgresql/15/main/pg_wal
touch /var/lib/postgresql/15/main/recovery.signal
systemctl start postgresql@15-main
