import os
import sqlite3
import time
import unicodedata
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuração: tudo vem de variáveis de ambiente, nada de credencial no código.
#
#   DB_HOST            -> se definido, usa PostgreSQL (ambiente Docker/deploy)
#   DB_PORT            -> porta do Postgres (padrão 5432)
#   POSTGRES_DB        -> nome do banco        (obrigatória com DB_HOST)
#   POSTGRES_USER      -> usuário do banco     (obrigatória com DB_HOST)
#   POSTGRES_PASSWORD  -> senha do banco       (obrigatória com DB_HOST)
#   SQLITE_PATH        -> arquivo SQLite usado SEM DB_HOST (dev local e testes)
#   CORS_ORIGINS       -> origens permitidas, separadas por vírgula (padrão "*")
#   HOST / PORT        -> endereço e porta do servidor (padrão 127.0.0.1:5000)
#   FLASK_DEBUG        -> "1" liga o modo debug (padrão desligado)
# ---------------------------------------------------------------------------
CORS(app, origins=os.environ.get("CORS_ORIGINS", "*").split(","))

DB_NAME = os.environ.get("SQLITE_PATH", "cyberflow.db")
STATUS_VALIDOS = ["Aberto", "Em Análise", "Resolvido"]


def usar_postgres():
    return bool(os.environ.get("DB_HOST"))


def _config_postgres():
    obrigatorias = ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")
    faltando = [v for v in obrigatorias if not os.environ.get(v)]
    if faltando:
        raise RuntimeError(
            "Variáveis de ambiente ausentes: " + ", ".join(faltando)
        )
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
    }


def get_db_connection():
    if usar_postgres():
        import psycopg2
        from psycopg2.extras import RealDictCursor

        return psycopg2.connect(cursor_factory=RealDictCursor, **_config_postgres())

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def executar(conn, sql, params=()):
    """Executa SQL escrito com '?' tanto no SQLite quanto no PostgreSQL."""
    if usar_postgres():
        cursor = conn.cursor()
        cursor.execute(sql.replace("?", "%s"), params)
        return cursor
    return conn.execute(sql, params)


def conectar_com_retry(tentativas=10, espera=2):
    """No Docker o Postgres pode demorar a ficar pronto; tenta de novo."""
    if not usar_postgres():
        return get_db_connection()

    import psycopg2

    for tentativa in range(1, tentativas + 1):
        try:
            return get_db_connection()
        except psycopg2.OperationalError:
            if tentativa == tentativas:
                raise
            time.sleep(espera)


def init_db():
    chave_primaria = (
        "SERIAL PRIMARY KEY" if usar_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    )
    conn = conectar_com_retry()
    executar(conn, f"""
        CREATE TABLE IF NOT EXISTS incidentes (
            id {chave_primaria},
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            data_hora TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aberto'
        )
    """)
    conn.commit()
    conn.close()


@app.route("/incidentes", methods=["POST"])
def criar_incidente():
    dados = request.get_json(silent=True)

    if not dados or not dados.get("titulo") or not dados.get("categoria"):
        return jsonify({"erro": "Campos 'titulo' e 'categoria' são obrigatórios"}), 400

    data_hora = dados.get("data_hora", datetime.now().isoformat(timespec="seconds"))

    conn = get_db_connection()
    cursor = executar(
        conn,
        "INSERT INTO incidentes (titulo, categoria, descricao, data_hora, status) "
        "VALUES (?, ?, ?, ?, ?) RETURNING id",
        (dados["titulo"], dados["categoria"], dados.get("descricao", ""), data_hora, "Aberto"),
    )
    novo_id = cursor.fetchone()["id"]
    conn.commit()
    conn.close()

    return jsonify({
        "id": novo_id,
        "titulo": dados["titulo"],
        "categoria": dados["categoria"],
        "descricao": dados.get("descricao", ""),
        "data_hora": data_hora,
        "status": "Aberto",
    }), 201


@app.route("/incidentes", methods=["GET"])
def listar_incidentes():
    conn = get_db_connection()
    incidentes = executar(conn, "SELECT * FROM incidentes ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(i) for i in incidentes]), 200


@app.route("/incidentes/<int:id>/status", methods=["PATCH"])
def atualizar_status(id):
    dados = request.get_json(silent=True)
    novo_status = dados.get("status") if dados else None

    if novo_status:
        novo_status = unicodedata.normalize("NFC", novo_status)

    if not novo_status or novo_status not in STATUS_VALIDOS:
        return jsonify({
            "erro": f"Status inválido. Use um dos: {', '.join(STATUS_VALIDOS)}"
        }), 400

    conn = get_db_connection()
    incidente = executar(conn, "SELECT * FROM incidentes WHERE id = ?", (id,)).fetchone()

    if incidente is None:
        conn.close()
        return jsonify({"erro": "Incidente não encontrado"}), 404

    executar(conn, "UPDATE incidentes SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()

    return jsonify({"id": id, "status": novo_status}), 200


if __name__ == "__main__":
    init_db()
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
