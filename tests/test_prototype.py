import pytest

import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Usa um banco SQLite isolado e impede conexão com PostgreSQL nos testes."""
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.setattr(app, "DB_NAME", str(tmp_path / "test_prototype.db"))
    app.app.config["TESTING"] = True
    app.init_db()

    with app.app.test_client() as test_client:
        yield test_client


def test_listar_modelos_retorna_seis_prototipos(client):
    response = client.get("/modelos-incidente")
    modelos = response.get_json()

    assert response.status_code == 200
    assert len(modelos) == 6
    assert {modelo["id"] for modelo in modelos} == {
        "phishing",
        "ransomware",
        "malware",
        "ddos",
        "vazamento-dados",
        "acesso-indevido",
    }


def test_clonar_modelo_phishing_cria_incidente(client):
    response = client.post(
        "/incidentes/modelos/phishing/clonar",
        json={"titulo": "E-mail suspeito recebido pelo Financeiro"},
    )
    incidente = response.get_json()

    assert response.status_code == 201
    assert incidente["id"] is not None
    assert incidente["titulo"] == "E-mail suspeito recebido pelo Financeiro"
    assert incidente["categoria"] == "Phishing"
    assert "Preservar a mensagem original" in incidente["descricao"]
    assert incidente["status"] == "Aberto"


def test_clonar_modelo_sem_personalizacao_usa_dados_originais(client):
    response = client.post("/incidentes/modelos/malware/clonar", json={})
    incidente = response.get_json()

    assert response.status_code == 201
    assert incidente["titulo"] == "Detecção de malware"
    assert incidente["categoria"] == "Malware"
    assert incidente["status"] == "Aberto"


def test_clonar_modelo_permite_personalizar_titulo_e_descricao(client):
    response = client.post(
        "/incidentes/modelos/ransomware/clonar",
        json={
            "titulo": "Ransomware no computador do setor financeiro",
            "descricao": "Arquivos do computador foram criptografados.",
        },
    )
    incidente = response.get_json()

    assert response.status_code == 201
    assert incidente["titulo"] == "Ransomware no computador do setor financeiro"
    assert incidente["descricao"] == "Arquivos do computador foram criptografados."
    assert incidente["categoria"] == "Ransomware"


def test_clonar_modelo_salva_incidente_na_listagem(client):
    clone_response = client.post(
        "/incidentes/modelos/ddos/clonar",
        json={"titulo": "Indisponibilidade no portal"},
    )
    incidente_criado = clone_response.get_json()

    list_response = client.get("/incidentes")
    incidentes = list_response.get_json()

    assert clone_response.status_code == 201
    assert list_response.status_code == 200
    assert len(incidentes) == 1
    assert incidentes[0]["id"] == incidente_criado["id"]
    assert incidentes[0]["titulo"] == "Indisponibilidade no portal"


def test_clonar_modelo_inexistente_retorna_404(client):
    response = client.post("/incidentes/modelos/modelo-inexistente/clonar", json={})

    assert response.status_code == 404
    assert response.get_json()["erro"] == "Modelo de incidente não encontrado"


def test_clonar_modelo_com_titulo_vazio_retorna_400(client):
    response = client.post(
        "/incidentes/modelos/phishing/clonar",
        json={"titulo": "   "},
    )

    assert response.status_code == 400
    assert "título" in response.get_json()["erro"]


def test_personalizacao_nao_altera_prototipo_original(client):
    primeira_resposta = client.post(
        "/incidentes/modelos/phishing/clonar",
        json={"titulo": "Primeiro incidente personalizado"},
    )
    segunda_resposta = client.post(
        "/incidentes/modelos/phishing/clonar",
        json={},
    )

    primeiro = primeira_resposta.get_json()
    segundo = segunda_resposta.get_json()

    assert primeira_resposta.status_code == 201
    assert segunda_resposta.status_code == 201
    assert primeiro["titulo"] == "Primeiro incidente personalizado"
    assert segundo["titulo"] == "Suspeita de phishing"
