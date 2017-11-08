FROM alpine:latest
RUN apk add --no-cache gettext bash nginx python3 uwsgi uwsgi-python3 openssl \
	&& pip3 install --upgrade pip
COPY app /app
RUN pip3 install -r /app/requirements.txt
RUN chown -R nginx:nginx /app \
    && mkdir -p /run/uwsgi/ \
    && chown -R nginx:nginx /run/uwsgi \
	&& chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx/nginx.conf
COPY nginx/nginx.conf.template /etc/nginx/nginx.conf.template
ARG HTTP_PASSWD
ENV HTTP_PASSWD=${HTTP_PASSWD}
RUN printf "admin:$(openssl passwd -crypt ${HTTP_PASSWD}\n)" >> /etc/nginx/.htpasswd
USER nginx
WORKDIR /app
CMD /app/entrypoint.sh
