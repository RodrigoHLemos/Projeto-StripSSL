FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    nginx \
    openssl \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY generate_certs.sh /app/generate_certs.sh
COPY entrypoint.sh /app/entrypoint.sh
COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static

RUN chmod +x /app/generate_certs.sh /app/entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/app/entrypoint.sh"]
