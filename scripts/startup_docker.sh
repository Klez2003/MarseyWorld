. ./.env
export DATABASE_URL='postgresql://postgres@postgres:5432'
export REDIS_URL='redis://redis:6379'
export PROXY_URL='http://opera-proxy:18080'
/etc/init.d/nginx start
gunicorn files.__main__:app
