from datetime import UTC, datetime
from functools import wraps
import os
import re

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

from firebase_service import (
    create_document,
    delete_document,
    find_one,
    firebase_status,
    list_documents,
    update_document,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PERFIS_VALIDOS = {"admin", "gerente", "funcionario"}
TIPOS_PUBLICACAO_VALIDOS = {"aviso", "noticia", "evento"}
STATUS_ROTAS = {"pendente", "em_andamento", "concluida"}


def limpar_texto(valor):
    return (valor or "").strip()


def processar_departamentos(valor):
    itens = [item.strip() for item in (valor or "").split(",")]
    departamentos = []
    vistos = set()

    for item in itens:
        chave = item.lower()
        if item and chave not in vistos:
            departamentos.append(item)
            vistos.add(chave)

    return departamentos


def usuario_logado():
    return session.get("usuario")


def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not usuario_logado():
            flash("Entre no sistema para continuar.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def perfil_obrigatorio(*perfis):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            usuario = usuario_logado()
            if not usuario:
                flash("Entre no sistema para continuar.", "warning")
                return redirect(url_for("login"))

            if usuario.get("perfil") not in perfis:
                flash("Você não tem permissão para acessar esta área.", "error")
                return redirect(url_for("dashboard"))

            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.template_filter("br_date")
def br_date(valor):
    if not valor:
        return "-"
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M")
    return str(valor)


def firestore_disponivel():
    ok, mensagem = firebase_status()
    if not ok:
        flash(f"Firebase indisponível: {mensagem}", "error")
    return ok


@app.route("/login", methods=["GET", "POST"])
def login():
    if usuario_logado():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        if not firestore_disponivel():
            return render_template("login.html")

        email = limpar_texto(request.form.get("email")).lower()
        if not EMAIL_REGEX.match(email):
            flash("Informe um e-mail válido.", "error")
            return render_template("login.html")

        usuario = find_one("usuarios", "email", email)
        if not usuario:
            flash("Usuário não encontrado no Firebase.", "error")
            return render_template("login.html")

        session["usuario"] = {
            "id": usuario["_id"],
            "nome": usuario.get("nome", "Usuário"),
            "email": usuario.get("email", email),
            "perfil": usuario.get("perfil", "funcionario"),
        }

        flash(f"Bem-vindo, {session['usuario']['nome']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_obrigatorio
def dashboard():
    if not firestore_disponivel():
        return render_template(
            "dashboard.html",
            usuario=session["usuario"],
            avisos=[],
            total_publicacoes=0,
            total_usuarios=0,
            total_rotas=0,
            rotas_pendentes=0,
            firebase_erro="Firebase indisponível.",
        )

    publicacoes = list_documents("publicacoes", order_by="criado_em", descending=True, limit=6)
    usuarios = list_documents("usuarios", order_by="nome")
    rotas = list_documents("rotas", order_by="data_saida", descending=True)
    rotas_pendentes = [rota for rota in rotas if rota.get("status") == "pendente"]

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        avisos=publicacoes,
        total_publicacoes=len(publicacoes),
        total_usuarios=len(usuarios),
        total_rotas=len(rotas),
        rotas_pendentes=len(rotas_pendentes),
        firebase_erro=None,
    )


@app.route("/usuarios")
@login_obrigatorio
@perfil_obrigatorio("admin", "gerente")
def listar_usuarios():
    if not firestore_disponivel():
        return render_template("usuarios.html", usuarios=[])

    usuarios = list_documents("usuarios", order_by="nome")
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/novo", methods=["GET", "POST"])
@login_obrigatorio
@perfil_obrigatorio("admin", "gerente")
def novo_usuario():
    if request.method == "POST":
        if not firestore_disponivel():
            return render_template("novo_usuario.html", dados_form=request.form)

        nome = limpar_texto(request.form.get("nome"))
        email = limpar_texto(request.form.get("email")).lower()
        cargo = limpar_texto(request.form.get("cargo"))
        departamento = limpar_texto(request.form.get("departamento"))
        perfil = limpar_texto(request.form.get("perfil")).lower()

        erros = []
        if len(nome) < 3:
            erros.append("Nome precisa ter pelo menos 3 caracteres.")
        if not EMAIL_REGEX.match(email):
            erros.append("E-mail inválido.")
        if len(cargo) < 2:
            erros.append("Cargo é obrigatório.")
        if len(departamento) < 2:
            erros.append("Departamento é obrigatório.")
        if perfil not in PERFIS_VALIDOS:
            erros.append("Perfil inválido.")
        if find_one("usuarios", "email", email):
            erros.append("Já existe um usuário com este e-mail.")

        if erros:
            for erro in erros:
                flash(erro, "error")
            return render_template("novo_usuario.html", dados_form=request.form)

        create_document(
            "usuarios",
            {
                "nome": nome,
                "email": email,
                "cargo": cargo,
                "departamento": departamento,
                "perfil": perfil,
                "criado_em": datetime.now(UTC),
            },
        )

        flash("Usuário criado no Firebase com sucesso.", "success")
        return redirect(url_for("listar_usuarios"))

    return render_template("novo_usuario.html", dados_form={})


@app.route("/usuarios/deletar/<id>")
@login_obrigatorio
@perfil_obrigatorio("admin")
def deletar_usuario(id):
    if session["usuario"]["id"] == id:
        flash("Você não pode remover o próprio usuário logado.", "error")
        return redirect(url_for("listar_usuarios"))

    if not firestore_disponivel():
        return redirect(url_for("listar_usuarios"))

    delete_document("usuarios", id)
    flash("Usuário removido do Firebase com sucesso.", "success")
    return redirect(url_for("listar_usuarios"))


@app.route("/publicacoes")
@login_obrigatorio
def listar_publicacoes():
    if not firestore_disponivel():
        return render_template("publicacoes.html", publicacoes=[])

    publicacoes = list_documents("publicacoes", order_by="criado_em", descending=True)
    return render_template("publicacoes.html", publicacoes=publicacoes)


@app.route("/publicacoes/nova", methods=["GET", "POST"])
@login_obrigatorio
@perfil_obrigatorio("admin", "gerente")
def nova_publicacao():
    if request.method == "POST":
        if not firestore_disponivel():
            return render_template("nova_publicacao.html", dados_form=request.form)

        titulo = limpar_texto(request.form.get("titulo"))
        conteudo = limpar_texto(request.form.get("conteudo"))
        tipo = limpar_texto(request.form.get("tipo")).lower()
        departamentos_lista = processar_departamentos(request.form.get("departamentos"))

        erros = []
        if len(titulo) < 5:
            erros.append("Título precisa ter pelo menos 5 caracteres.")
        if len(conteudo) < 10:
            erros.append("Conteúdo precisa ter pelo menos 10 caracteres.")
        if tipo not in TIPOS_PUBLICACAO_VALIDOS:
            erros.append("Tipo inválido.")
        if not departamentos_lista:
            erros.append("Informe pelo menos um departamento.")

        if erros:
            for erro in erros:
                flash(erro, "error")
            return render_template("nova_publicacao.html", dados_form=request.form)

        create_document(
            "publicacoes",
            {
                "titulo": titulo,
                "conteudo": conteudo,
                "tipo": tipo,
                "departamentos": departamentos_lista,
                "autor": session["usuario"]["nome"],
                "criado_em": datetime.now(UTC),
            },
        )

        flash("Publicação criada no Firebase com sucesso.", "success")
        return redirect(url_for("listar_publicacoes"))

    return render_template("nova_publicacao.html", dados_form={})


@app.route("/rotas")
@login_obrigatorio
def listar_rotas():
    if not firestore_disponivel():
        return render_template("rotas.html", rotas=[])

    rotas = list_documents("rotas", order_by="data_saida", descending=True)
    return render_template("rotas.html", rotas=rotas)


@app.route("/rotas/nova", methods=["GET", "POST"])
@login_obrigatorio
@perfil_obrigatorio("admin", "gerente")
def nova_rota():
    if request.method == "POST":
        if not firestore_disponivel():
            return render_template("nova_rota.html", dados_form=request.form)

        motorista = limpar_texto(request.form.get("motorista"))
        caminhao = limpar_texto(request.form.get("caminhao"))
        origem = limpar_texto(request.form.get("origem"))
        destino = limpar_texto(request.form.get("destino"))
        carga = limpar_texto(request.form.get("carga"))
        data_saida = limpar_texto(request.form.get("data_saida"))

        erros = []
        for campo, nome in [
            (motorista, "Motorista"),
            (caminhao, "Caminhão"),
            (origem, "Origem"),
            (destino, "Destino"),
            (carga, "Carga"),
            (data_saida, "Data de saída"),
        ]:
            if not campo:
                erros.append(f"{nome} é obrigatório.")

        if erros:
            for erro in erros:
                flash(erro, "error")
            return render_template("nova_rota.html", dados_form=request.form)

        create_document(
            "rotas",
            {
                "motorista": motorista,
                "caminhao": caminhao,
                "origem": origem,
                "destino": destino,
                "carga": carga,
                "data_saida": data_saida,
                "status": "pendente",
                "criado_em": datetime.now(UTC),
            },
        )

        flash("Rota criada no Firebase com sucesso.", "success")
        return redirect(url_for("listar_rotas"))

    return render_template("nova_rota.html", dados_form={})


@app.route("/rotas/<id>/<status>")
@login_obrigatorio
@perfil_obrigatorio("admin", "gerente")
def alterar_status_rota(id, status):
    if status not in STATUS_ROTAS:
        flash("Status inválido.", "error")
        return redirect(url_for("listar_rotas"))

    if not firestore_disponivel():
        return redirect(url_for("listar_rotas"))

    update_document("rotas", id, {"status": status})
    flash("Status atualizado no Firebase.", "success")
    return redirect(url_for("listar_rotas"))


if __name__ == "__main__":
    app.run(debug=True)
