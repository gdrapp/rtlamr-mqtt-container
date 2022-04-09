FROM golang:alpine3.14 AS builder

ENV CGO_ENABLED=0

RUN apk update && apk add --no-cache git

RUN go install -v github.com/bemasher/rtlamr@latest

FROM python:3-alpine

RUN apk update \
    && apk upgrade \
    && apk add tini

COPY --from=builder /go/bin/rtlamr /usr/local/bin

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY rtlamr-mqtt.py .

ENTRYPOINT ["/sbin/tini", "--", "python3", "/usr/src/app/rtlamr-mqtt.py"]