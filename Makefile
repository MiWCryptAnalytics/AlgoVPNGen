IMAGE_NAME='algovpngen'
PORT=8001
DEVPORT=8000

image:
	docker build -t ${IMAGE_NAME} .

runlocal:
	docker run --rm -e PORT=8001 -p ${DEVPORT}:${PORT} -it ${IMAGE_NAME}

runint:
	docker run --rm -e PORT=${PORT} -p ${DEVPORT}:${PORT} -it ${IMAGE_NAME} /bin/bash