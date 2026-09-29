#!/usr/bin/env python3
"""
Simulador de Comportamento da Vítima
Executa navegação e autenticação no Internet Banking
"""

import sys
import time
import requests
import urllib3

# Suprime avisos de certificados autoassinados em ambiente de laboratório
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVER_HOST = "banco.lab.local"
URL_HTTP = f"http://{SERVER_HOST}"
URL_HTTPS = f"https://{SERVER_HOST}"

VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
AZUL = "\033[94m"
CIANO = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


class VitimaClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        self.logado = False
        self.token_sessao = None

    def banner(self):
        print(f"\n{CIANO}{BOLD}===================================================={RESET}")
        print(f"{CIANO}{BOLD}   SIMULADOR DE CLIENTE VÍTIMA - CEUB SECUREBANK     {RESET}")
        print(f"{CIANO}{BOLD}===================================================={RESET}")
        print(f"IP da Vítima:  172.20.0.30")
        print(f"Servidor Alvo: {SERVER_HOST} (172.20.0.10)")
        if self.token_sessao:
            print(f"Sessão Ativa:  {VERDE}{self.token_sessao}{RESET}")
        else:
            print(f"Sessão:        {AMARELO}Não autenticado{RESET}")
        print(f"{CIANO}----------------------------------------------------{RESET}\n")

    def acessar_home(self, url=URL_HTTP):
        print(f"[*] Requisitando: {url} ...")
        try:
            r = self.session.get(url, verify=False, timeout=5, allow_redirects=True)
            print(f"{VERDE}[+] Resposta recebida! Código HTTP: {r.status_code}{RESET}")
            print(f"    URL Final: {r.url}")
            print(f"    Protocolo Usado: {BOLD}{'HTTPS (Criptografado)' if r.url.startswith('https') else 'HTTP (TEXTO CLARO / DESPROTEGIDO!)'}{RESET}")
            
            # Verifica cabeçalhos de segurança
            hsts = r.headers.get("Strict-Transport-Security")
            if hsts:
                print(f"    {VERDE}[ESCUDO HSTS DETECTADO]: {hsts}{RESET}")
            else:
                print(f"    {VERMELHO}[ALERTA]: Cabeçalho HSTS AUSENTE! (Suscetível a SSL Stripping){RESET}")
            return r
        except Exception as e:
            print(f"{VERMELHO}[-] Erro ao conectar ao servidor: {e}{RESET}")
            return None

    def fazer_login(self, usuario="vitima", senha="senha123", url_base=URL_HTTP):
        print(f"\n[*] Tentando autenticar como '{usuario}' em {url_base}/login ...")
        payload = {"usuario": usuario, "senha": senha}
        try:
            r = self.session.post(f"{url_base}/login", data=payload, verify=False, timeout=5, allow_redirects=True)
            cookies = self.session.cookies.get_dict()
            if "session_id" in cookies:
                self.token_sessao = cookies["session_id"]
                self.logado = True
                print(f"{VERDE}{BOLD}[+] LOGIN REALIZADO COM SUCESSO!{RESET}")
                print(f"    Cookie 'session_id' obtido: {BOLD}{CIANO}{self.token_sessao}{RESET}")
                
                # Inspeciona flags do cookie recebido
                for c in self.session.cookies:
                    if c.name == "session_id":
                        print(f"    Flags do Cookie: Secure={c.secure}, HttpOnly={'HttpOnly' in c._rest.keys() or getattr(c, 'has_nonstandard_attr', lambda x: False)('HttpOnly')}")
                return True
            else:
                print(f"{VERMELHO}[-] Falha no login ou credenciais rejeitadas.{RESET}")
                return False
        except Exception as e:
            print(f"{VERMELHO}[-] Erro na requisição de login: {e}{RESET}")
            return False

    def consultar_saldo(self, url_base=URL_HTTP):
        print(f"\n[*] Acessando Dashboard em {url_base}/dashboard ...")
        try:
            r = self.session.get(f"{url_base}/dashboard", verify=False, timeout=5)
            if "SALDO DISPONÍVEL" in r.text or "Alexsandro" in r.text:
                print(f"{VERDE}[+] Dashboard acessado com sucesso!{RESET}")
                if "HTTP (Não Criptografado)" in r.text:
                    print(f"    {VERMELHO}{BOLD}[PERIGO]: O Dashboard foi entregue via HTTP texto claro!{RESET}")
                else:
                    print(f"    {VERDE}[SEGURO]: O Dashboard foi entregue via HTTPS.{RESET}")
            elif r.status_code == 302 or "login" in r.url:
                print(f"{AMARELO}[!] Sessão expirada ou não autenticada.{RESET}")
            else:
                print(f"[-] Resposta inesperada (Status {r.status_code})")
        except Exception as e:
            print(f"{VERMELHO}[-] Erro ao consultar dashboard: {e}{RESET}")

    def transferir_pix(self, destinatario="farmacia@pix.com", valor=150.00, url_base=URL_HTTP):
        print(f"\n[*] Enviando PIX legítimo da vítima de R$ {valor:.2f} para '{destinatario}'...")
        payload = {"destinatario": destinatario, "valor": valor}
        try:
            r = self.session.post(f"{url_base}/transferir", data=payload, verify=False, timeout=5, allow_redirects=True)
            if r.status_code == 200:
                print(f"{VERDE}[+] PIX de R$ {valor:.2f} realizado com sucesso!{RESET}")
            else:
                print(f"{VERMELHO}[-] Falha na transferência: Código {r.status_code}{RESET}")
        except Exception as e:
            print(f"{VERMELHO}[-] Erro na transferência: {e}{RESET}")

    def loop_automatico(self, intervalo=4):
        print(f"\n{AMARELO}[*] INICIANDO MODO AUTOMÁTICO (Simulação de Tráfego Contínuo)...{RESET}")
        print(f"Pressione CTRL+C para interromper a qualquer momento.\n")
        
        # 1. Faz login inicial
        self.fazer_login()
        
        contador = 1
        try:
            while True:
                print(f"\n--- [Ciclo #{contador}] Simulação de navegação do usuário ---")
                self.consultar_saldo()
                time.sleep(intervalo)
                contador += 1
        except KeyboardInterrupt:
            print(f"\n{AMARELO}[!] Modo automático finalizado pelo usuário.{RESET}")


def menu():
    vitima = VitimaClient()
    
    while True:
        vitima.banner()
        print("Opções disponíveis:")
        print("  1) Acessar site via HTTP (http://banco.lab.local)")
        print("  2) Acessar site via HTTPS (https://banco.lab.local)")
        print("  3) Fazer Login (usuário: vitima / senha: senha123)")
        print("  4) Consultar Saldo e Extrato")
        print("  5) Realizar Transferência PIX legítima (R$ 150,00)")
        print("  6) Executar Simulação Completa Automatizada (Login + Navegação)")
        print("  7) Modo Loop Contínuo (Ideal para demonstração durante o ataque)")
        print("  0) Sair")
        
        escolha = input("\nEscolha uma opção [0-7]: ").strip()
        
        if escolha == "1":
            vitima.acessar_home(URL_HTTP)
        elif escolha == "2":
            vitima.acessar_home(URL_HTTPS)
        elif escolha == "3":
            vitima.fazer_login()
        elif escolha == "4":
            vitima.consultar_saldo()
        elif escolha == "5":
            dest = input("Informe o favorecido (Padrão: Farmacia Popular): ").strip() or "Farmacia Popular"
            val = input("Informe o valor (Padrão: 150.00): ").strip() or "150.00"
            vitima.transferir_pix(dest, float(val))
        elif escolha == "6":
            print(f"\n{BOLD}[*] Executando fluxo completo da vítima...{RESET}")
            vitima.acessar_home(URL_HTTP)
            time.sleep(1)
            vitima.fazer_login()
            time.sleep(1)
            vitima.consultar_saldo()
        elif escolha == "7":
            vitima.loop_automatico()
        elif escolha == "0":
            print("\nEncerrando simulador da vítima. Até logo!")
            break
        else:
            print(f"\n{VERMELHO}Opção inválida.{RESET}")
            
        input(f"\n{BOLD}Pressione ENTER para continuar...{RESET}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        v = VitimaClient()
        v.loop_automatico()
    elif len(sys.argv) > 1 and sys.argv[1] == "--login":
        v = VitimaClient()
        v.fazer_login()
        v.consultar_saldo()
    else:
        menu()
