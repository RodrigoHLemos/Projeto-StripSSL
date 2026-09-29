#!/bin/bash
# Menu interativo de ataque do container Atacante (172.20.0.20)

clear
echo "=========================================================="
echo "          CONSOLE DO ATACANTE (KALI / BETTERCAP)          "
echo "                     CEUB SECUREBANK                      "
echo "=========================================================="
echo "Selecione a ação ofensiva:"
echo " 1) Iniciar Bettercap com SSL Stripping + ARP Spoofing"
echo " 2) Iniciar Sniffer de Credenciais e Cookies (Scapy)"
echo " 3) Executar Sequestro de Sessão e Transferência Fraudulenta"
echo " 4) Iniciar Bettercap no Modo Console Interativo"
echo " 5) Visualizar Status Atual das Contas (API)"
echo " 6) Abrir Shell Bash"
echo " 0) Sair"
echo "=========================================================="
read -p "Opção [1-6]: " opcao

case "$opcao" in
    1)
        /app/iniciar_bettercap.sh
        ;;
    2)
        python3 /app/sniffer_credenciais.py
        ;;
    3)
        python3 /app/sequestro_sessao.py
        ;;
    4)
        /app/bettercap
        ;;
    5)
        curl -s http://172.20.0.10/api/status | python3 -m json.tool
        ;;
    6)
        /bin/bash
        ;;
    *)
        echo "Saindo..."
        ;;
esac
