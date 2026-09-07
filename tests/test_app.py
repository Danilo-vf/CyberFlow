import pytest

import app


@pytest.fixture
def client(tmp_path):
    """
    Cria um banco SQLite temporário para cada teste.
    Assim, os testes não alteram o banco real do projeto.
    """
    app.DB_NAME = str(tmp_path / "test_cyberflow.db")
    app.init_db()
    app.app.config["TESTING"] = True

    with app.app.test_client() as client:
        yield client


def test_criar_incidente_com_dados_validos(client):
    payload = {
        "titulo": "Tentativa de phishing",
        "categoria": "Phishing",
        "descricao": "E-mail suspeito recebido por um colaborador.",
        "data_hora": "2026-09-07T14:00:00",
    }

    response = client.post("/incidentes", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["id"] is not None
    assert data["titulo"] == payload["titulo"]
    assert data["categoria"] == payload["categoria"]
    assert data["descricao"] == payload["descricao"]
    assert data["data_hora"] == payload["data_hora"]
    assert data["status"] == "Aberto"


def test_criar_incidente_sem_titulo_retorna_400(client):
    payload = {
        "categoria": "Malware",
        "descricao": "Incidente sem título.",
    }

    response = client.post("/incidentes", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "titulo" in data["erro"]


def test_criar_incidente_sem_categoria_retorna_400(client):
    payload = {
        "titulo": "Arquivo suspeito",
        "descricao": "Incidente sem categoria.",
    }

    response = client.post("/incidentes", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "categoria" in data["erro"]


def test_listar_incidentes_retorna_lista_vazia(client):
    response = client.get("/incidentes")

    assert response.status_code == 200
    assert response.get_json() == []


def test_listar_incidentes_retorna_incidente_cadastrado(client):
    payload = {
        "titulo": "Acesso não autorizado",
        "categoria": "Acesso",
        "descricao": "Tentativa de acesso fora do horário.",
        "data_hora": "2026-09-07T14:10:00",
    }

    create_response = client.post("/incidentes", json=payload)
    created = create_response.get_json()

    response = client.get("/incidentes")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] == created["id"]
    assert data[0]["titulo"] == payload["titulo"]
    assert data[0]["categoria"] == payload["categoria"]
    assert data[0]["descricao"] == payload["descricao"]
    assert data[0]["status"] == "Aberto"


def test_atualizar_status_para_resolvido(client):
    payload = {
        "titulo": "Malware detectado",
        "categoria": "Malware",
        "descricao": "Arquivo malicioso identificado.",
    }

    create_response = client.post("/incidentes", json=payload)
    created = create_response.get_json()

    incident_id = created["id"]

    response = client.patch(
        f"/incidentes/{incident_id}/status",
        json={"status": "Resolvido"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == incident_id
    assert data["status"] == "Resolvido"


def test_atualizar_status_invalido_retorna_400(client):
    payload = {
        "titulo": "Tentativa de invasão",
        "categoria": "Segurança",
        "descricao": "Tentativa de acesso indevido.",
    }

    create_response = client.post("/incidentes", json=payload)
    created = create_response.get_json()

    incident_id = created["id"]

    response = client.patch(
        f"/incidentes/{incident_id}/status",
        json={"status": "Cancelado"},
    )
    data = response.get_json()

    assert response.status_code == 400
    assert "Status inválido" in data["erro"]


def test_atualizar_status_incidente_inexistente_retorna_404(client):
    response = client.patch(
        "/incidentes/999/status",
        json={"status": "Resolvido"},
    )
    data = response.get_json()

    assert response.status_code == 404
    assert data["erro"] == "Incidente não encontrado"