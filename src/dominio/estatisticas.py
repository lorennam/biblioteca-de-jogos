from functools import reduce

from src.dominio.regras import ESTADOS_VALIDOS, normalizar_status, status_valido

filtrar_por_status = lambda jogos, status: (
    list(filter(lambda jogo: jogo["status"] == normalizar_status(status), jogos))
    if status_valido(status)
    else []
)

total_de_jogos = lambda jogos: len(jogos)

total_de_horas = lambda jogos: reduce(lambda acc, jogo: jogo["horas_jogadas"] + acc, jogos, 0.0)

horas_por_status = lambda jogos, status: total_de_horas(filtrar_por_status(jogos, status))

todos_os_generos = lambda jogos: reduce(lambda acc, jogo: acc + jogo["genero"], jogos, [])

contagem_por_genero = lambda jogos: reduce(lambda acc, g: {**acc, g: acc.get(g, 0) + 1}, todos_os_generos(jogos), {})

resumo = lambda jogos: {
    "total_jogos": total_de_jogos(jogos),
    "total_horas": total_de_horas(jogos),
    "horas_por_status": dict(map(lambda s: (s, horas_por_status(jogos, s)), ESTADOS_VALIDOS)),
    "contagem_por_genero": contagem_por_genero(jogos),
}