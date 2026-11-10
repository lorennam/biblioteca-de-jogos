from src.dominio.estatisticas import filtrar_por_status, total_de_jogos, total_de_horas, horas_por_status, todos_os_generos, contagem_por_genero, resumo

jogos = [
    {"nome": "Zelda", "status": "jogando", "horas_jogadas": 10.0, "genero": ["Aventura", "RPG"]},
    {"nome": "Hades", "status": "finalizado", "horas_jogadas": 100.0, "genero": ["RPG", "Roguelike"]},
    {"nome": "Celeste", "status": "jogando", "horas_jogadas": 30.0, "genero": ["Plataforma"]},
]

print(resumo([]))  # esperado: tudo zerado, contagem {}