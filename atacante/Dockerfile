FROM bettercap/bettercap:latest

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-requests \
    py3-beautifulsoup4 \
    iptables \
    curl \
    bash \
    tcpdump \
    iproute2 \
    net-tools \
    && pip install --no-cache-dir --break-system-packages scapy

WORKDIR /app

COPY sslstrip.cap /app/sslstrip.cap
COPY sniffer_credenciais.py /app/sniffer_credenciais.py
COPY sequestro_sessao.py /app/sequestro_sessao.py
COPY iniciar_bettercap.sh /app/iniciar_bettercap.sh
COPY menu_atacante.sh /app/menu_atacante.sh

RUN chmod +x /app/*.sh /app/*.py

ENTRYPOINT []
CMD ["tail", "-f", "/dev/null"]
