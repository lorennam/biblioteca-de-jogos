import sqlite3
import tempfile
from pathlib import Path

from src.armazenamento.backlog_sqlite import (
    ler_backlog,
    salvar_jogo,
    atualizar_horas,
    remover_jogo,
    ERROS_ARMAZENAMENTO,
)
from src.dominio.regras import somar_horas

pasta = Path(tempfile.mkdtemp())
arq = pasta / "sub" / "teste.db"

zelda = {"id": 7, "nome": "Pokémon", "capa": "https://x/y.jpg",
         "genero": ["Aventura", "RPG"], "status": "quero_jogar", "horas_jogadas": 0.0}
sem_genero = {"id": 9, "nome": "Outro", "capa": "c", "genero": [],
              "status": "jogando", "horas_jogadas": 0.0}

assert ler_backlog(arq) == []                          
assert salvar_jogo(zelda, arq) == zelda                
salvar_jogo(sem_genero, arq)
assert ler_backlog(arq) == [zelda, sem_genero]         

atualizado = atualizar_horas(somar_horas(zelda, 2.5), arq)
assert atualizado["horas_jogadas"] == 2.5
assert ler_backlog(arq)[0]["horas_jogadas"] == 2.5
assert ler_backlog(arq)[1]["horas_jogadas"] == 0.0     
atualizar_horas(somar_horas(ler_backlog(arq)[0], 1.0), arq)
assert ler_backlog(arq)[0]["horas_jogadas"] == 3.5     

salvar_jogo({**zelda, "status": "finalizado", "horas_jogadas": 0.0}, arq)
lista = ler_backlog(arq)
assert len(lista) == 2
assert lista[0]["status"] == "finalizado" and lista[0]["horas_jogadas"] == 3.5

assert salvar_jogo({**sem_genero, "id": 11, "status": "  JOGANDO "}, arq)["status"] == "jogando"
assert ler_backlog(arq)[-1]["status"] == "jogando"     
novo_arq = pasta / "invalido.db"
try:
    salvar_jogo({**zelda, "status": "abacaxi"}, novo_arq)
    print("ERRO: deveria ter recusado o status")
except ValueError:
    assert not novo_arq.exists()                     
try:
    salvar_jogo({**zelda, "status": None}, novo_arq)
    print("ERRO: deveria ter recusado o status None")
except ValueError:
    pass
assert ValueError in ERROS_ARMAZENAMENTO

assert remover_jogo(9, arq) == 9
assert list(map(lambda j: j["id"], ler_backlog(arq))) == [7, 11]
assert remover_jogo(12345, arq) == 12345               
assert len(ler_backlog(arq)) == 2

arq.write_text("isso não é um banco")
try:
    ler_backlog(arq)
    print("ERRO: deveria ter falhado")
except ERROS_ARMAZENAMENTO:
    pass

print("armazenamento: ok")