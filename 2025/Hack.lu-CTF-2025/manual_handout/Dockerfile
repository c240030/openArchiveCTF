FROM python:3.14.0-slim@sha256:5cfac249393fa6c7ebacaf0027a1e127026745e603908b226baa784c52b9d99b

USER root
RUN apt-get update && apt-get install -y socat

WORKDIR /app
COPY server.py .

USER root

ENTRYPOINT ["/bin/sh"]
CMD ["-c", "socat tcp-listen:1024,fork,reuseaddr system:\"python3 /app/server.py\""]