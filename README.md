# Banco de Preços - API PNCP & IBGE

Este projeto é um protótipo de **Banco de Preços de Compras Públicas** utilizando a API oficial do Portal Nacional de Contratações Públicas (PNCP) combinada com dados de população do IBGE para fornecer filtros comparativos por porte populacional de municípios.

## Tecnologias Utilizadas
*   **Python 3.10+**
*   **FastAPI** - Framework web assíncrono moderno e rápido
*   **SQLAlchemy 2.0 (Async)** - ORM para persistência dos dados
*   **aiosqlite** - Driver SQLite assíncrono
*   **HTTPX** - Cliente HTTP assíncrono para consumir APIs externas
*   **Pydantic v2** - Validação de dados e parsing de JSON

---

## Como Instalar e Rodar o Projeto

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure as variáveis de ambiente:**
    Copie as variáveis do arquivo `.env.example` para um novo arquivo `.env`:
    ```bash
    cp .env.example .env
    ```

3.  **Rode o Script de Carga de Dados (IBGE):**
    Este script cria o banco SQLite local (`banco_precos.db`) e baixa a base oficial de municípios do IBGE com as respectivas populações da estimativa oficial, aplicando as faixas de porte do IBGE.
    ```bash
    python seed_db.py
    ```

4.  **Inicie o Servidor FastAPI:**
    ```bash
    python app/main.py
    ```
    Ou via Uvicorn:
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Acesse a Documentação da API:**
    *   Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Lógica do Porte de Município (IBGE)

A comparabilidade das contratações públicas baseia-se na classificação oficial do IBGE para porte dos municípios:
*   **Pequeno Porte I:** Até 20.000 habitantes.
*   **Pequeno Porte II:** De 20.001 a 50.000 habitantes.
*   **Médio Porte:** De 50.001 a 100.000 habitantes.
*   **Grande Porte:** Acima de 100.000 habitantes.

Ao ativar a busca com o filtro de **Porte Comparável**, o sistema:
1. Identifica a população e o porte do município do usuário comprador (ex: Município A, SP - 35.000 hab. -> *Pequeno Porte II*).
2. Filtra a busca do PNCP apenas para compras realizadas por municípios do **mesmo estado** (SP) que também tenham o porte *Pequeno Porte II*.

---

## Rotas Principais da API

*   `GET /api/municipalities/`
    Lista e busca municípios brasileiros cadastrados na base (filtros por nome, UF e porte).
*   `GET /api/prices/search`
    Realiza a pesquisa de preços praticados no PNCP aplicando filtros de palavra-chave, UF e porte comparável de cidade.
