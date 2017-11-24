#!/bin/sh
envsubst '\$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
#nginx && uwsgi --ini /app/app.ini --http :5000 --gevent 1000 --http-websockets
nginx && gunicorn --worker-class eventlet -w 1 app:app gunicorn --bind=127.0.0.1:5000 --enable-stdio-inheritance --access-logfile - --error-logfile -
