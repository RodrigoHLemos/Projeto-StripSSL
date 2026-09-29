FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-requests \
    python3-pip \
    curl \
    lynx \
    iproute2 \
    net-tools \
    iputils-ping \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY simular_usuario.py /app/simular_usuario.py
COPY acessar_banco.sh /app/acessar_banco.sh
COPY menu_vitima.sh /app/menu_vitima.sh

RUN chmod +x /app/*.sh /app/*.py

CMD ["tail", "-f", "/dev/null"]
