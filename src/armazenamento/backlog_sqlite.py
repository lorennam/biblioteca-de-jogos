import json
import sqlite3
from pathlib import Path

from src.dominio.regras import normalizar_status, status_valido

CAMINHO_PADRAO = Path(__file__).resolve().parents[2] / "dados" / "backlog.db"

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

SQL_SALVAR = """
INSERT INTO jogos (id, nome, capa, genero, status, horas_jogadas)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET status = excluded.status
"""

SQL_ATUALIZAR_HORAS = "UPDATE jogos SET horas_jogadas = ? WHERE id = ?"

SQL_REMOVER = "DELETE FROM jogos WHERE id = ?"

SQL_LER = """
SELECT id, nome, capa, genero, status, horas_jogadas
FROM jogos
ORDER BY rowid
"""

lancar = lambda erro: (_ for _ in ()).throw(erro)

validar_jogo = lambda jogo: (
    {**jogo, "status": normalizar_status(jogo["status"])}
    if status_valido(jogo["status"])
    else lancar(ValueError(f"Status inválido: {jogo['status']!r}"))
)

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

conectar = lambda caminho: (
    caminho.parent.mkdir(parents=True, exist_ok=True),
    sqlite3.connect(caminho),
)[-1]

preparar = lambda conn: (conn.execute(SQL_TABELA), conn)[-1]

abrir = lambda caminho: preparar(conectar(caminho))

executar = lambda sql, parametros, caminho: (
    lambda conn: (conn.execute(sql, parametros), conn.commit(), conn.close())
)(abrir(caminho))

ler_backlog = lambda caminho=CAMINHO_PADRAO: (
    lambda conn: (
        lambda linhas: (conn.close(), list(map(linha_para_jogo, linhas)))[-1]
    )(conn.execute(SQL_LER).fetchall())
)(abrir(caminho))

salvar_jogo = lambda jogo, caminho=CAMINHO_PADRAO: (
    lambda valido: (
        executar(SQL_SALVAR, jogo_para_linha(valido), caminho),
        valido,
    )[-1]
)(validar_jogo(jogo))

atualizar_horas = lambda jogo, caminho=CAMINHO_PADRAO: (
    executar(SQL_ATUALIZAR_HORAS, (jogo["horas_jogadas"], jogo["id"]), caminho),
    jogo,
)[-1]

remover_jogo = lambda id_jogo, caminho=CAMINHO_PADRAO: (
    executar(SQL_REMOVER, (id_jogo,), caminho),
    id_jogo,
)[-1]