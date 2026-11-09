# I/O: obter token e consultar a IGDB
import requests

URL_TOKEN = "https://id.twitch.tv/oauth2/token"
URL_JOGOS = "https://api.igdb.com/v4/games"

CABECALHO_CLIENT_ID = "Client-ID"
CABECALHO_AUTORIZACAO = "Authorization"

obter_token = lambda client_id, client_secret:(
    lambda resposta: (
        resposta.json().get("access_token") if resposta.status_code == 200 else None
    )
)(
    requests.post(
        URL_TOKEN,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    )
)

montar_consulta = lambda texto: f'search "{texto}";\nfields id, name, cover.url, genres.name;\nlimit 10;'

consultar_jogos = lambda token, client_id, texto: (
    lambda resposta: (
        resposta.json() if resposta.status_code == 200 else None
    )
)(
    requests.post(
        URL_JOGOS,
        headers={
            CABECALHO_CLIENT_ID: client_id,
            CABECALHO_AUTORIZACAO: f"Bearer {token}",
        },
        data=montar_consulta(texto),
        timeout=10,
    )
)