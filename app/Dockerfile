# Uses alpine:edge for newer node.js (heroku)
FROM alpine:edge
# Install node and python for heroku/app
RUN apk add --no-cache gcc musl-dev gettext bash nginx python3 python3-dev uwsgi    \
                     uwsgi-python3 uwsgi-gevent3 openssl nodejs-current yarn expect \
                     file libev py3-gevent && pip3 install --upgrade pip
# Install app to container
COPY app /app
RUN pip3 install -r /app/requirements.txt
RUN chown -R nginx:nginx /app \
    && mkdir -p /run/uwsgi/ \
    && chown -R nginx:nginx /run/uwsgi \
	&& chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx/nginx.conf
COPY nginx/nginx.conf.template /etc/nginx/nginx.conf.template
# Configure a password (to protect instance during dev)
ARG HTTP_PASSWD
ENV HTTP_PASSWD=${HTTP_PASSWD}
RUN printf "admin:$(openssl passwd -crypt ${HTTP_PASSWD}\n)" >> /etc/nginx/.htpasswd
# Embed Heroku API Key into container
ARG HEROKU_API_KEY
ENV HEROKU_API_KEY=${HEROKU_API_KEY}
# Install Heroku CLI
RUN yarn global add heroku-cli
#USER nginx
WORKDIR /app
# Run the web app (flask + uwsgi + nginx)
CMD /app/entrypoint.sh
