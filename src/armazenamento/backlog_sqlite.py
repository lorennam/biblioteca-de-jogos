import json
import sqlite3
from pathlib import Path

# Raiz do projeto = duas pastas acima de src/armazenamento/
CAMINHO_PADRAO = Path(__file__).resolve().parents[2] / "dados" / "backlog.db"

# Tupla para o app.py usar em `except ERROS_ARMAZENAMENTO:`
ERROS_ARMAZENAMENTO = (OSError, sqlite3.Error, ValueError)

SQL_TABELA = """
CREATE TABLE IF NOT EXISTS jogos (
    id            INTEGER PRIMARY KEY,
    nome          TEXT NOT NULL,
    capa          TEXT NOT NULL,
    genero        TEXT NOT NULL,
    status        TEXT NOT NULL,
    horas_jogadas REAL NOT NULL DEFAULT 0.0
)
"""

# Jogo novo entra; jogo que já existe (mesmo id) só troca de status,
# preservando as horas já jogadas. Isso resolve as duplicatas.
SQL_SALVAR = """
INSERT INTO jogos (id, nome, capa, genero, status, horas_jogadas)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET status = excluded.status
"""

SQL_LER = """
SELECT id, nome, capa, genero, status, horas_jogadas
FROM jogos
ORDER BY rowid
"""

# --- Funções puras: conversão entre dicionário do jogo e linha da tabela ---

# A lista de gêneros vira texto JSON dentro de uma única coluna.
jogo_para_linha = lambda jogo: (
    jogo["id"],
    jogo["nome"],
    jogo["capa"],
    json.dumps(jogo["genero"], ensure_ascii=False),
    jogo["status"],
    jogo["horas_jogadas"],
)

linha_para_jogo = lambda linha: {
    "id": linha[0],
    "nome": linha[1],
    "capa": linha[2],
    "genero": json.loads(linha[3]),
    "status": linha[4],
    "horas_jogadas": linha[5],
}

# --- I/O ---

# Cria a pasta se preciso e abre a conexão.
conectar = lambda caminho: (
    caminho.parent.mkdir(parents=True, exist_ok=True),
    sqlite3.connect(caminho),
)[-1]

# Garante que a tabela exista e devolve a mesma conexão.
preparar = lambda conn: (conn.execute(SQL_TABELA), conn)[-1]

abrir = lambda caminho: preparar(conectar(caminho))

# Lê todos os jogos, na ordem em que foram adicionados.
ler_backlog = lambda caminho=CAMINHO_PADRAO: (
    lambda conn: (
        lambda linhas: (conn.close(), list(map(linha_para_jogo, linhas)))[-1]
    )(conn.execute(SQL_LER).fetchall())
)(abrir(caminho))

# Insere (ou atualiza o status de) um jogo e devolve o próprio jogo.
salvar_jogo = lambda jogo, caminho=CAMINHO_PADRAO: (
    lambda conn: (
        conn.execute(SQL_SALVAR, jogo_para_linha(jogo)),
        conn.commit(),
        conn.close(),
        jogo,
    )[-1]
)(abrir(caminho))