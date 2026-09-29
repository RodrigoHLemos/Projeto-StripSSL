#!/bin/bash
set -e

CERT_DIR="/etc/ssl/certs"
mkdir -p "$CERT_DIR"

if [ ! -f "$CERT_DIR/banco.crt" ]; then
    echo "[+] Gerando certificado TLS autoassinado para o CEUB SecureBank..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERT_DIR/banco.key" \
        -out "$CERT_DIR/banco.crt" \
        -subj "/C=BR/ST=DF/L=Brasilia/O=CEUB/OU=SegurancaDaInformacao/CN=banco.lab.local" \
        -addext "subjectAltName=DNS:banco.lab.local,DNS:app.lab.local,DNS:localhost,IP:172.20.0.10"
        
    echo "[+] Certificado gerado com sucesso em $CERT_DIR/banco.crt"
    chmod 644 "$CERT_DIR/banco.crt"
    chmod 600 "$CERT_DIR/banco.key"
fi
