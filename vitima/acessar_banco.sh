#!/bin/bash
# Script rápido de acesso via cURL no container da vítima

echo "=== [Vítima] Teste de Requisição HTTP ==="
echo "[*] Enviando GET para http://banco.lab.local ..."
curl -i -s -L http://banco.lab.local | head -n 25

echo -e "\n=== [Vítima] Teste de Requisição HTTPS ==="
echo "[*] Enviando GET para https://banco.lab.local ..."
curl -i -s -k https://banco.lab.local | head -n 25
