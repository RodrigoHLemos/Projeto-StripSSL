#!/bin/bash
set -e

echo "=== [CEUB SecureBank Server] Inicializando Servidor Alvo ==="

# Gera certificados TLS caso não existam
/app/generate_certs.sh

# Copia o certificado para a pasta compartilhada /certs (para que a vítima possa confiar se quiser)
mkdir -p /certs
cp /etc/ssl/certs/banco.crt /certs/banco.crt || true

# Inicia o serviço Nginx em background
echo "[+] Iniciando Nginx (Portas 80 HTTP e 443 HTTPS)..."
nginx

# Inicia a aplicação Flask via Gunicorn
echo "[+] Iniciando Backend Flask Gunicorn na porta 5000..."
exec gunicorn --workers 2 --bind 127.0.0.1:5000 --access-logfile - --error-logfile - app:app
