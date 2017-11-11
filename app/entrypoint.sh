#!/bin/sh
envsubst '\$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
nginx && uwsgi --ini /app/app.ini --gevent 100
