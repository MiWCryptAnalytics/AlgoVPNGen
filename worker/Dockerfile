FROM alpine:latest
LABEL name="algovpngenworker"
RUN apk add --no-cache bash openssl openssh-client libffi python py-pip git gcc musl-dev python-dev libffi-dev openssl-dev make
RUN pip install virtualenv
RUN git clone https://www.github.com/trailofbits/algo
WORKDIR /algo
RUN python -m virtualenv env && source env/bin/activate && python -m pip install -U pip && python -m pip install -r requirements.txt
COPY worker/doit.sh /algo
CMD ./doit.sh