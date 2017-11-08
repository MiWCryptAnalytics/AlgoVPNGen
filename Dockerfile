FROM alpine:latest
RUN apk add --no-cache gettext bash nginx python3 uwsgi uwsgi-python3 \
	&& pip3 install --upgrade pip
COPY app /app
RUN pip3 install -r /app/requirements.txt
RUN chown -R nginx:nginx /app \
    && mkdir -p /run/uwsgi/ \
    && chown -R nginx:nginx /run/uwsgi \
    && mkdir -p /var/tmp/nginx \
    && chown -R nginx:nginx /var/tmp/nginx
COPY nginx/nginx.conf.template /etc/nginx/nginx.conf.template
WORKDIR /app
CMD /app/entrypoint.sh