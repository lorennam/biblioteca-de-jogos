ESTADOS_VALIDOS = ("jogando", "quero_jogar", "finalizado")

normalizar_status = lambda status: status.strip().lower()

status_valido = lambda status: (
    isinstance(status, str) and normalizar_status(status) in ESTADOS_VALIDOS
)

somar_horas = lambda jogo, horas: {
    **jogo,
    "horas_jogadas": jogo["horas_jogadas"] + horas,
}