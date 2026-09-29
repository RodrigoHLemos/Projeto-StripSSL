#!/bin/bash
set -e

echo "=========================================================="
echo "      INICIALIZANDO LABORATÓRIO CEUB - SSL STRIPPING      "
echo "=========================================================="

echo "[+] Subindo a stack Docker Compose..."
docker compose up -d --build

echo "[+] Aguardando inicialização dos serviços..."
sleep 3

echo -e "\n[+] Status dos Containers:"
docker compose ps

echo -e "\n=========================================================="
echo "   LABORATÓRIO INICIALIZADO COM SUCESSO!                  "
echo "=========================================================="
echo "Topologia da Rede (172.20.0.0/24):"
echo " - Servidor Web:  172.20.0.10 (http://localhost:8080 no host)"
echo " - Atacante:      172.20.0.20 (Container: lab_atacante)"
echo " - Vítima:        172.20.0.30 (Container: lab_vitima)"
echo ""
echo "Comandos rápidos para entrar nos containers:"
echo " Atacante: docker exec -it lab_atacante /app/menu_atacante.sh"
echo " Vítima:   docker exec -it lab_vitima /app/menu_vitima.sh"
echo "=========================================================="
