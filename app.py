from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import unicodedata
from datetime import datetime

app = Flask(__name__)
CORS(app)  # permite que o frontend (outra origem/porta) chame essa API

DB_NAME = "cyberflow.db"
STATUS_VALIDOS = ["Aberto", "Em Análise", "Resolvido"]


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    cursor = conn.execute(
        "INSERT INTO incidentes (titulo, categoria, descricao, data_hora, status) VALUES (?, ?, ?, ?, ?)",
        (dados["titulo"], dados["categoria"], dados.get("descricao", ""), data_hora, "Aberto"),
    )
    conn.commit()
    novo_id = cursor.lastrowid
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
    incidentes = conn.execute("SELECT * FROM incidentes ORDER BY id DESC").fetchall()
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
    incidente = conn.execute("SELECT * FROM incidentes WHERE id = ?", (id,)).fetchone()

    if incidente is None:
        conn.close()
        return jsonify({"erro": "Incidente não encontrado"}), 404

    conn.execute("UPDATE incidentes SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()

    return jsonify({"id": id, "status": novo_status}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000) 