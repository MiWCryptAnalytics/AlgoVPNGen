#!/bin/sh
envsubst '\$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
#nginx && uwsgi --ini /app/app.ini --http :5000 --gevent 1000 --http-websockets
nginx && uwsgi --plugins http,python3,gevent3 --http :5000 --gevent 1000 --http-websockets --master --wsgi-file app.py --callable app
