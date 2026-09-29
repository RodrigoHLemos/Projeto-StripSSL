#!/bin/bash
# Menu interativo do container da Vítima

clear
echo "=================================================="
echo "          CONTAINER DA VÍTIMA (172.20.0.30)       "
echo "=================================================="
echo "Selecione o que deseja executar:"
echo " 1) Iniciar Simulador Interativo Python (Recomendado)"
echo " 2) Iniciar Modo Automático em Loop Contínuo"
echo " 3) Navegar no Internet Banking usando navegador LYNX (Terminal)"
echo " 4) Fazer Login Rápido via cURL"
echo " 5) Abrir Shell Bash"
echo " 0) Sair"
echo "=================================================="
read -p "Opção [1-5]: " opcao

case "$opcao" in
    1)
        python3 /app/simular_usuario.py
        ;;
    2)
        python3 /app/simular_usuario.py --auto
        ;;
    3)
        lynx http://banco.lab.local
        ;;
    4)
        /app/acessar_banco.sh
        ;;
    5)
        /bin/bash
        ;;
    *)
        echo "Saindo..."
        ;;
esac
