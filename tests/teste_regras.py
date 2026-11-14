import src.dominio.estatisticas as estatisticas
from src.dominio.regras import (
    ESTADOS_VALIDOS,
    normalizar_status,
    status_valido,
    somar_horas,
)

assert ESTADOS_VALIDOS == ("jogando", "quero_jogar", "finalizado")
assert normalizar_status("  JOGANDO ") == "jogando"
assert status_valido("  JOGANDO ") is True
assert status_valido("abacaxi") is False
assert status_valido("") is False
assert status_valido(None) is False

jogo = {"id": 1, "horas_jogadas": 2.0}
novo = somar_horas(jogo, 1.5)
assert novo["horas_jogadas"] == 3.5
assert jogo["horas_jogadas"] == 2.0   
assert novo is not jogo

assert estatisticas.ESTADOS_VALIDOS is ESTADOS_VALIDOS
assert estatisticas.normalizar_status is normalizar_status

assert estatisticas.todos_os_generos([{"genero": ["A", "B"]}, {"genero": ["C"]}]) == ["A", "B", "C"]

lista = [{"status": "jogando"}, {"status": "finalizado"}]
assert estatisticas.filtrar_por_status(lista, "  JOGANDO ") == [{"status": "jogando"}]
assert estatisticas.filtrar_por_status(lista, "abacaxi") == []
assert estatisticas.filtrar_por_status(lista, None) == []

jogos = [
    {"status": "jogando", "horas_jogadas": 10.0, "genero": ["RPG"]},
    {"status": "finalizado", "horas_jogadas": 5.0, "genero": ["RPG", "Action"]},
]
r = estatisticas.resumo(jogos)
assert r["total_jogos"] == 2 and r["total_horas"] == 15.0
assert r["horas_por_status"] == {"jogando": 10.0, "quero_jogar": 0.0, "finalizado": 5.0}
assert r["contagem_por_genero"] == {"RPG": 2, "Action": 1}
assert estatisticas.resumo([])["total_jogos"] == 0

print("regras e estatisticas: ok")