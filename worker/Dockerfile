FROM alpine:latest
LABEL name="algovpngenworker"
ENV PYTHONIOENCODING="utf-8"
ENV LANG="en_US.UTF-8"
ENV LC_CTYPE="en_US.UTF-8"
RUN apk add --no-cache bash openssl openssh-client libffi python py-pip git gcc musl-dev python-dev libffi-dev zip openssl-dev make
RUN pip install virtualenv
RUN git clone https://www.github.com/trailofbits/algo
WORKDIR /algo
RUN python -m virtualenv env && source env/bin/activate && python -m pip install -U pip && python -m pip install -r requirements.txt
COPY worker/doit.sh /algo
CMD ./doit.sh