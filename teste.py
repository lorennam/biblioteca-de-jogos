from src.dominio.traducao import limpar_texto_busca
from src.dominio.estatisticas import contagem_por_genero
from src.igdb.cliente import montar_consulta

assert limpar_texto_busca("The Witcher") == "The Witcher"
assert limpar_texto_busca('  "Zelda"  ') == "Zelda"
assert limpar_texto_busca("     ") is None
print("limpar_texto_busca: ok")

consulta = montar_consulta("Zelda")
assert "Zelda" in consulta
assert len(consulta.splitlines()) == 3
print("montar_consulta: ok")

jogo_sem_genero = {"nome": "X", "genero": [], "horas_jogadas": 0.0, "status": "quero_jogar"}
jogo_com_genero = {"nome": "Y", "genero": ["Action", "RPG"], "horas_jogadas": 1.0, "status": "jogando"}

assert contagem_por_genero([jogo_sem_genero]) == {}
assert contagem_por_genero([jogo_sem_genero, jogo_com_genero]) == {"Action": 1, "RPG": 1}
print("contagem_por_genero: ok")

print("Todos os testes passaram.")