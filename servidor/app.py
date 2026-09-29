#!/usr/bin/env python3
"""
CEUB SecureBank - Aplicação Web para Simulação de SSL Stripping e Mitigação HSTS
Projeto de Pesquisa em Segurança da Informação - CEUB
Autor: Alexsandro Patrício dos Santos Júnior
"""

import os
import uuid
import datetime
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Estado global da simulação (em memória para facilidade de demonstração e reset)
ESTADO_INICIAL = {
    "modo_seguranca": "vulneravel",  # "vulneravel" ou "mitigado"
    "usuarios": {
        "vitima": {
            "nome": "Alexsandro Patrício (Vítima)",
            "senha": "senha123",
            "saldo": 5000.00,
            "chave_pix": "alexsandro@ceub.br",
            "conta": "12345-6",
            "agencia": "0001"
        },
        "atacante": {
            "nome": "Invasor Malicioso (Atacante)",
            "senha": "hackersupersecret",
            "saldo": 50.00,
            "chave_pix": "atacante@fraude.org",
            "conta": "99999-9",
            "agencia": "6666"
        }
    },
    "sessoes": {},  # token -> username
    "extrato": [
        {
            "data": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%d/%m/%Y %H:%M"),
            "tipo": "Crédito",
            "descricao": "Depósito Salarial",
            "valor": 5000.00,
            "origem": "Folha de Pagamento CEUB",
            "destino": "Alexsandro Patrício (Vítima)"
        }
    ]
}

# Clona o estado inicial
dados = {
    "modo_seguranca": ESTADO_INICIAL["modo_seguranca"],
    "usuarios": {u: dict(v) for u, v in ESTADO_INICIAL["usuarios"].items()},
    "sessoes": {},
    "extrato": list(ESTADO_INICIAL["extrato"])
}


def obter_usuario_logado():
    token = request.cookies.get("session_id")
    if token and token in dados["sessoes"]:
        username = dados["sessoes"][token]
        return username, dados["usuarios"].get(username)
    return None, None


@app.after_request
def aplicar_politicas_seguranca(response):
    """
    Aplica controles criptográficos e cabeçalhos de segurança conforme o modo ativo.
    No modo 'mitigado': Adiciona HSTS (RFC 6797) e proteções ISO/IEC 27002.
    No modo 'vulneravel': Deixa sem HSTS permitindo interceptação e rebaixamento SSL.
    """
    response.headers["X-Lab-Modo"] = dados["modo_seguranca"]
    
    if dados["modo_seguranca"] == "mitigado":
        # RFC 6797 - HTTP Strict Transport Security
        # Instrução imperativa para o navegador só se comunicar via HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    else:
        # Modo vulnerável: remove ou omite HSTS deliberadamente
        response.headers.pop("Strict-Transport-Security", None)
        
    return response


@app.route("/")
def index():
    usuario, info = obter_usuario_logado()
    if usuario:
        return redirect(url_for("dashboard"))
    return render_template("index.html", modo=dados["modo_seguranca"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("senha", "").strip()
        
        user_data = dados["usuarios"].get(username)
        if user_data and user_data["senha"] == password:
            # Gera token de identificador de sessão
            session_id = f"sess_{uuid.uuid4().hex}"
            dados["sessoes"][session_id] = username
            
            resp = make_response(redirect(url_for("dashboard")))
            
            # CONFIGURAÇÃO DO COOKIE DE SESSÃO:
            # - Modo Vulnerável: Secure=False (permite envio por HTTP claro), HttpOnly=False
            # - Modo Mitigado (ISO/IEC 27002 / OWASP): Secure=True, HttpOnly=True, SameSite=Strict
            if dados["modo_seguranca"] == "mitigado":
                resp.set_cookie(
                    "session_id",
                    session_id,
                    max_age=3600,
                    secure=True,
                    httponly=True,
                    samesite="Strict",
                    path="/"
                )
            else:
                resp.set_cookie(
                    "session_id",
                    session_id,
                    max_age=3600,
                    secure=False,      # VULNERÁVEL! Enviado em conexões HTTP sem TLS
                    httponly=False,    # VULNERÁVEL! Acessível via scripts
                    samesite="Lax",
                    path="/"
                )
            return resp
        else:
            flash("Credenciais inválidas! Tente usuário: vitima / senha: senha123", "danger")
            return redirect(url_for("login"))
            
    return render_template("login.html", modo=dados["modo_seguranca"])


@app.route("/dashboard")
def dashboard():
    usuario, info = obter_usuario_logado()
    if not usuario:
        flash("Acesso não autorizado! Faça login primeiro.", "warning")
        return redirect(url_for("login"))
        
    token = request.cookies.get("session_id")
    protocolo = "HTTPS (Seguro)" if request.is_secure or request.headers.get("X-Forwarded-Proto") == "https" else "HTTP (Inseguro / Texto Claro!)"
    
    return render_template(
        "dashboard.html",
        usuario=usuario,
        info=info,
        token=token,
        protocolo=protocolo,
        extrato=dados["extrato"],
        modo=dados["modo_seguranca"],
        total_vitima=dados["usuarios"]["vitima"]["saldo"],
        total_atacante=dados["usuarios"]["atacante"]["saldo"]
    )


@app.route("/transferir", methods=["POST"])
def transferir():
    usuario, info = obter_usuario_logado()
    if not usuario:
        return jsonify({"erro": "Não autenticado! Cookie de sessão ausente ou inválido."}), 401
        
    destinatario = request.form.get("destinatario", "").strip()
    try:
        valor = float(request.form.get("valor", 0))
    except (ValueError, TypeError):
        flash("Valor inválido para transferência.", "danger")
        return redirect(url_for("dashboard"))
        
    if valor <= 0 or valor > info["saldo"]:
        flash(f"Saldo insuficiente ou valor inválido! Saldo atual: R$ {info['saldo']:.2f}", "danger")
        return redirect(url_for("dashboard"))
        
    # Executa a transferência
    info["saldo"] -= valor
    
    # Se o destinatário for o atacante ou chave PIX do atacante, credita nele
    if destinatario in ["atacante", "atacante@fraude.org", "Invasor Malicioso (Atacante)"] or "atacante" in destinatario.lower():
        dados["usuarios"]["atacante"]["saldo"] += valor
        dest_nome = "Invasor Malicioso (Atacante)"
    else:
        dest_nome = destinatario
        
    transacao = {
        "data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "tipo": "Débito (PIX)",
        "descricao": f"Transferência para {dest_nome}",
        "valor": valor,
        "origem": info["nome"],
        "destino": dest_nome
    }
    dados["extrato"].insert(0, transacao)
    
    # Se for requisição JSON/API (ex: script do atacante executando session hijacking)
    if request.is_json or request.headers.get("Accept") == "application/json" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "sucesso",
            "mensagem": f"Transferência de R$ {valor:.2f} realizada com sucesso para {dest_nome}!",
            "saldo_restante": info["saldo"],
            "transacao": transacao
        })
        
    flash(f"Transferência PIX de R$ {valor:.2f} enviada para {dest_nome} com sucesso!", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    token = request.cookies.get("session_id")
    if token and token in dados["sessoes"]:
        del dados["sessoes"][token]
    resp = make_response(redirect(url_for("login")))
    resp.delete_cookie("session_id")
    return resp


@app.route("/seguranca")
def seguranca():
    return render_template("seguranca.html", modo=dados["modo_seguranca"])


@app.route("/api/alternar-seguranca", methods=["POST"])
def alternar_seguranca():
    novo_modo = request.form.get("modo") or request.json.get("modo") if request.is_json else None
    if novo_modo in ["vulneravel", "mitigado"]:
        dados["modo_seguranca"] = novo_modo
    else:
        dados["modo_seguranca"] = "mitigado" if dados["modo_seguranca"] == "vulneravel" else "vulneravel"
        
    flash(f"Modo de Segurança alterado para: {dados['modo_seguranca'].upper()}", "info")
    return redirect(request.referrer or url_for("seguranca"))


@app.route("/api/reset", methods=["POST", "GET"])
def reset():
    """Restaura o estado inicial do laboratório para nova demonstração"""
    global dados
    dados = {
        "modo_seguranca": ESTADO_INICIAL["modo_seguranca"],
        "usuarios": {u: dict(v) for u, v in ESTADO_INICIAL["usuarios"].items()},
        "sessoes": {},
        "extrato": list(ESTADO_INICIAL["extrato"])
    }
    flash("Laboratório resetado para o estado inicial!", "warning")
    return redirect(url_for("dashboard"))


@app.route("/api/status")
def api_status():
    """Endpoint para ferramentas de automação e monitoramento do ataque"""
    return jsonify({
        "modo_seguranca": dados["modo_seguranca"],
        "saldo_vitima": dados["usuarios"]["vitima"]["saldo"],
        "saldo_atacante": dados["usuarios"]["atacante"]["saldo"],
        "total_sessoes_ativas": len(dados["sessoes"]),
        "sessoes_ativas": list(dados["sessoes"].keys()),
        "ultimas_transacoes": dados["extrato"][:5]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
