import time
import requests

URL_TOKEN = "https://id.twitch.tv/oauth2/token"
URL_JOGOS = "https://api.igdb.com/v4/games"

CABECALHO_CLIENT_ID = "Client-ID"
CABECALHO_AUTORIZACAO = "Authorization"

MARGEM_SEGURANCA = 60

TIPOS_PERMITIDOS = (0, 1, 2, 4, 8, 9, 10)

calcular_expiracao = lambda agora, expires_in, margem=MARGEM_SEGURANCA: (
    agora + expires_in - margem
)

token_valido = lambda token, expira_em, agora: bool(token) and agora < expira_em

montar_registro_token = lambda dados, agora: {
    "token": dados.get("access_token"),
    "expira_em": calcular_expiracao(agora, dados.get("expires_in", 0)),
}

consultar_com_renovacao = lambda consultar, renovar, token: (
    lambda brutos: (
        brutos
        if (brutos is not None or not token)
        else consultar(renovar())
    )
)(consultar(token))

obter_token = lambda client_id, client_secret: (
    lambda resposta: (
        montar_registro_token(resposta.json(), time.time())
        if resposta.status_code == 200
        else None
    )
)(
    requests.post(
        URL_TOKEN,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
)

montar_consulta = lambda texto: (
    f'search "{texto}";\n'
    f'fields id, name, cover.url, genres.name, game_type;\n'
    f'where game_type = ({",".join(map(str, TIPOS_PERMITIDOS))});\n'
    f'limit 10;'
)

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