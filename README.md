# CyberFlow 🛡️

Plataforma de Gestão de Incidentes de Cibersegurança — projeto da disciplina de Integração DevOps (Ciência da Computação, UniCEUB).

O CyberFlow apoia a organização, o registro, a classificação, o acompanhamento e o encerramento de incidentes de segurança da informação (ex: suspeita de vazamento de dados, máquina infectada, tentativa de acesso indevido).

## Sobre o projeto

Esta é a entrega do **Marco 1 (A1)**: um MVP funcional com código-fonte, interface de interação e banco de dados, além de testes automatizados e uma pipeline de Integração Contínua.

Fluxo coberto nesta etapa:

1. **Registro do incidente** — o colaborador abre um chamado informando título, categoria, descrição e data/hora.
2. **Acompanhamento de status** — o incidente pode ser atualizado entre `Aberto`, `Em Análise` e `Resolvido`.
3. **Listagem** — todos os incidentes registrados ficam visíveis numa tabela, para consulta e triagem.

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python + Flask |
| Banco de dados | SQLite |
| Frontend | HTML, CSS e JavaScript puro |
| Testes | Pytest |
| CI/CD | GitHub Actions |
| Versionamento | Git (estratégia Trunk-Based) |

## Estrutura do repositório

```
CyberFlow/
├── .github/
│   └── workflows/
│       └── ci.yml          # Pipeline de CI (build + testes a cada push/PR)
├── tests/
│   └── test_app.py         # Testes automatizados da API
├── app.py                  # Backend Flask + conexão SQLite
├── index.html               # Interface de cadastro e listagem
├── style.css                 # Estilo da interface
├── app.js                    # Consumo da API pelo frontend
├── requirements.txt          # Dependências Python
├── .gitignore
├── CONTRIBUTING.md           # Regras de contribuição do grupo
└── README.md
```

## Como rodar localmente

### Pré-requisitos

- [Python 3.11+](https://www.python.org/downloads/) instalado
- [Git](https://git-scm.com/) instalado
- Um navegador qualquer

### 1. Clonar o repositório

```bash
git clone https://github.com/Danilo-vf/CyberFlow.git
cd CyberFlow
```

### 2. Criar e ativar um ambiente virtual

```bash
python -m venv venv
```

Ativação, de acordo com o seu terminal:

```bash
# Git Bash (Windows) ou Linux/Mac
source venv/Scripts/activate      # Git Bash no Windows
source venv/bin/activate          # Linux/Mac

# Prompt de Comando (cmd) no Windows
venv\Scripts\activate.bat

# PowerShell no Windows
venv\Scripts\Activate.ps1
```

Você deve ver `(venv)` no início da linha do terminal.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar o backend

```bash
python app.py
```

O servidor sobe em `http://localhost:5000` e já cria o banco `cyberflow.db` automaticamente na primeira execução (vazio — é esperado, cada máquina tem seu próprio banco local).

Deixe esse terminal aberto rodando.

### 5. Abrir o frontend

Em outra janela, abra o arquivo `index.html` diretamente no navegador (duplo clique, ou `start index.html` no Git Bash). A interface já está configurada para se comunicar com a API em `localhost:5000`.

### 6. Testar

Cadastre um incidente pela tela e confirme que ele aparece na listagem logo em seguida.

## Endpoints da API

### Criar um incidente

```
POST /incidentes
Content-Type: application/json

{
  "titulo": "E-mail suspeito",
  "categoria": "Phishing",
  "descricao": "Link estranho recebido por um colaborador",
  "data_hora": "2026-09-08T10:00:00"
}
```

Resposta (`201 Created`):

```json
{
  "id": 1,
  "titulo": "E-mail suspeito",
  "categoria": "Phishing",
  "descricao": "Link estranho recebido por um colaborador",
  "data_hora": "2026-09-08T10:00:00",
  "status": "Aberto"
}
```

`titulo` e `categoria` são obrigatórios; sem eles, a API responde `400`.

### Listar incidentes

```
GET /incidentes
```

Resposta (`200 OK`): lista com todos os incidentes cadastrados, mais recentes primeiro.

### Atualizar o status de um incidente

```
PATCH /incidentes/<id>/status
Content-Type: application/json

{
  "status": "Em Análise"
}
```

Valores aceitos: `"Aberto"`, `"Em Análise"`, `"Resolvido"`. Retorna `400` para status inválido e `404` se o incidente não existir.

## Rodando os testes

Com o ambiente virtual ativado:

```bash
pytest
```

Os testes cobrem criação de incidentes, validação de campos obrigatórios, listagem, atualização de status e os principais casos de erro (status inválido, incidente inexistente). Eles usam um banco SQLite temporário próprio, sem afetar o `cyberflow.db` local.

## Pipeline de CI

A cada `push` ou `pull request` para a `main`, o GitHub Actions:

1. Faz o checkout do código.
2. Instala as dependências do `requirements.txt`.
3. Roda a suíte de testes com `pytest`.

Se algum teste falhar, a pipeline fica vermelha e o merge para a `main` é bloqueado. A branch `main` também exige aprovação de outro colaborador antes de qualquer merge.

## Fluxo de contribuição

Este projeto segue a estratégia **Trunk-Based**:

- Toda mudança nasce numa branch curta a partir da `main` atualizada (`feat/nome-da-funcionalidade`, `fix/nome-do-problema`).
- Commits seguem o padrão `feat:`, `fix:`, `test:` (ex: `feat: adicionar rota de atualização de status`).
- Mudanças vão para a `main` apenas via Pull Request, com aprovação de outro membro do grupo e checks de CI passando.
- Branches são apagadas após o merge.

Mais detalhes em [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Equipe

| Nome | Responsabilidade |
|---|---|
| Danilo Vilela | Infraestrutura/Ops — repositório, proteção de branch e pipeline de CI |
| Guilherme Borges | Backend e banco de dados |
| Filipe Portela | Frontend |
| Caio Peryco | Qualidade/QA — testes automatizados |
