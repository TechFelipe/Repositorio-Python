import os
import sqlite3
from functools import wraps

import requests
from flask import Flask, jsonify, redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-dev-troque-em-producao")
app.config["DEBUG"] = False

DATABASE = os.path.join(os.path.dirname(__file__), "tarefas.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'Pendente'
                CHECK(status IN ('Pendente', 'Em andamento', 'Concluída')),
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar o painel.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def validar_tarefa(titulo, descricao, status):
    titulo = (titulo or "").strip()
    descricao = (descricao or "").strip()
    status = (status or "Pendente").strip()

    if not titulo:
        return None, "O título da tarefa é obrigatório."

    if len(titulo) > 120:
        return None, "O título deve ter no máximo 120 caracteres."

    if status not in ("Pendente", "Em andamento", "Concluída"):
        return None, "Status inválido."

    return (titulo, descricao, status), None


def tarefa_para_dict(row):
    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "descricao": row["descricao"] or "",
        "status": row["status"],
        "usuario_id": row["usuario_id"],
    }


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "danger")
            return render_template("registro.html")

        if len(senha) < 6:
            flash("A senha deve possuir pelo menos 6 caracteres.", "danger")
            return render_template("registro.html")

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, generate_password_hash(senha))
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Este e-mail já está cadastrado.", "danger")
            return render_template("registro.html")

        conn.close()
        flash("Conta criada com sucesso. Agora faça login.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        conn = get_db()
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if usuario and check_password_hash(usuario["senha"], senha):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("dashboard"))

        flash("E-mail ou senha incorretos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    tarefas = conn.execute(
        "SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC",
        (session["usuario_id"],)
    ).fetchall()
    conn.close()

    return render_template("dashboard.html", tarefas=tarefas)


@app.route("/nova_tarefa", methods=["GET", "POST"])
@login_required
def nova_tarefa():
    if request.method == "POST":
        dados, erro = validar_tarefa(
            request.form.get("titulo"),
            request.form.get("descricao"),
            request.form.get("status")
        )
        if erro:
            flash(erro, "danger")
            return render_template("nova_tarefa.html")

        titulo, descricao, status = dados
        conn = get_db()
        conn.execute(
            "INSERT INTO tarefas (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)",
            (titulo, descricao, status, session["usuario_id"])
        )
        conn.commit()
        conn.close()

        flash("Tarefa criada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    return render_template("nova_tarefa.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    conn = get_db()
    tarefa = conn.execute(
        "SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"])
    ).fetchone()

    if not tarefa:
        conn.close()
        flash("Tarefa não encontrada.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        dados, erro = validar_tarefa(
            request.form.get("titulo"),
            request.form.get("descricao"),
            request.form.get("status")
        )
        if erro:
            conn.close()
            flash(erro, "danger")
            return render_template("editar.html", tarefa=tarefa)

        titulo, descricao, status = dados
        conn.execute(
            "UPDATE tarefas SET titulo = ?, descricao = ?, status = ? "
            "WHERE id = ? AND usuario_id = ?",
            (titulo, descricao, status, id, session["usuario_id"])
        )
        conn.commit()
        conn.close()

        flash("Tarefa atualizada com sucesso!", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("editar.html", tarefa=tarefa)


@app.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    conn = get_db()
    conn.execute(
        "DELETE FROM tarefas WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"])
    )
    conn.commit()
    conn.close()

    flash("Tarefa excluída.", "success")
    return redirect(url_for("dashboard"))


# Retorna somente tarefas do usuário logado em JSON.
@app.route("/api/tarefas", methods=["GET"])
@login_required
def api_tarefas():
    status = request.args.get("status", "").strip()

    conn = get_db()
    if status in ("Pendente", "Em andamento", "Concluída"):
        rows = conn.execute(
            "SELECT * FROM tarefas WHERE usuario_id = ? AND status = ? ORDER BY id DESC",
            (session["usuario_id"], status)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC",
            (session["usuario_id"],)
        ).fetchall()
    conn.close()

    return jsonify([tarefa_para_dict(row) for row in rows])


# API REST: criar tarefa.
@app.route("/api/tarefas", methods=["POST"])
@login_required
def api_criar_tarefa():
    data = request.get_json(silent=True) or {}
    dados, erro = validar_tarefa(data.get("titulo"), data.get("descricao"), data.get("status"))
    if erro:
        return jsonify({"erro": erro}), 400

    titulo, descricao, status = dados
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tarefas (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)",
        (titulo, descricao, status, session["usuario_id"])
    )
    conn.commit()
    tarefa = conn.execute(
        "SELECT * FROM tarefas WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()

    return jsonify(tarefa_para_dict(tarefa)), 201


# API REST: atualizar tarefa.
@app.route("/api/tarefas/<int:id>", methods=["PUT"])
@login_required
def api_editar_tarefa(id):
    data = request.get_json(silent=True) or {}

    conn = get_db()
    tarefa = conn.execute(
        "SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"])
    ).fetchone()

    if not tarefa:
        conn.close()
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    dados, erro = validar_tarefa(
        data.get("titulo", tarefa["titulo"]),
        data.get("descricao", tarefa["descricao"]),
        data.get("status", tarefa["status"])
    )
    if erro:
        conn.close()
        return jsonify({"erro": erro}), 400

    titulo, descricao, status = dados
    conn.execute(
        "UPDATE tarefas SET titulo = ?, descricao = ?, status = ? "
        "WHERE id = ? AND usuario_id = ?",
        (titulo, descricao, status, id, session["usuario_id"])
    )
    conn.commit()

    atualizado = conn.execute(
        "SELECT * FROM tarefas WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    return jsonify(tarefa_para_dict(atualizado))


# API REST: excluir tarefa.
@app.route("/api/tarefas/<int:id>", methods=["DELETE"])
@login_required
def api_excluir_tarefa(id):
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM tarefas WHERE id = ? AND usuario_id = ?",
        (id, session["usuario_id"])
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"erro": "Tarefa não encontrada."}), 404

    return jsonify({"mensagem": "Tarefa excluída com sucesso."})


# Dados para o gráfico de progresso.
@app.route("/api/progresso")
@login_required
def api_progresso():
    conn = get_db()
    rows = conn.execute(
        "SELECT status, COUNT(*) AS total FROM tarefas "
        "WHERE usuario_id = ? GROUP BY status",
        (session["usuario_id"],)
    ).fetchall()
    conn.close()

    contagem = {"Pendente": 0, "Em andamento": 0, "Concluída": 0}
    for row in rows:
        contagem[row["status"]] = row["total"]

    return jsonify(contagem)


@app.context_processor
def inject_user():
    return {"usuario_nome": session.get("usuario_nome")}


def buscar_frase():
    try:
        resposta = requests.get(
            "https://api.adviceslip.com/advice",
            timeout=5,
            headers={"Accept": "application/json"}
        )
        resposta.raise_for_status()
        return resposta.json()["slip"]["advice"]
    except (requests.RequestException, KeyError, ValueError):
        return "Cada pequena tarefa concluída é um passo em direção ao seu objetivo."


@app.context_processor
def inject_advice():
    # Mantém a chamada somente quando houver usuário logado.
    if "usuario_id" in session:
        return {"frase_motivacional": buscar_frase()}
    return {"frase_motivacional": None}


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
