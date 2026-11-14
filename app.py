import streamlit as st
import time
import requests
import pandas as pd
from src.igdb.cliente import obter_token, consultar_jogos, token_valido, consultar_com_renovacao
from src.dominio.traducao import limpar_texto_busca, traduzir_jogo
from src.dominio.estatisticas import filtrar_por_status, resumo
from src.armazenamento.backlog_sqlite import ler_backlog, salvar_jogo, ERROS_ARMAZENAMENTO

st.set_page_config(
    page_title="Biblioteca de Jogos",
    page_icon="🎮",
    layout="wide",
)

credenciais_ok = "client_id" in st.secrets and "client_secret" in st.secrets

if not credenciais_ok:
    st.error("Credenciais da IGDB não encontradas em .streamlit/secrets.toml")
    st.stop()

client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

ESTADO_INICIAL = {
    "token": None,
    "token_expira_em": 0.0,
    "backlog": [],
    "backlog_carregado": False,
}

list(map(lambda par: st.session_state.setdefault(par[0], par[1]), ESTADO_INICIAL.items()))

ABAS = ("Buscar", "Jogando", "Quero jogar", "Finalizados", "Estatísticas")

st.sidebar.title("🎮 Biblioteca de Jogos")
aba_atual = st.sidebar.radio("Navegação", ABAS)

texto_busca = (
    st.text_input("Buscar jogo", placeholder="Ex.: Zelda, Hollow Knight...")
    if aba_atual == "Buscar"
    else None
)

texto_limpo = limpar_texto_busca(texto_busca) if texto_busca else None

# Pede um token novo, guarda token e vencimento na sessão e devolve o token
# (ou None se a Twitch recusar; nesse caso a sessão não é alterada).
renovar_token = lambda: (
    lambda registro: (
        (
            st.session_state.update(
                token=registro["token"], token_expira_em=registro["expira_em"]
            ),
            registro["token"],
        )[-1]
        if registro
        else None
    )
)(obter_token(client_id, client_secret))

# Reaproveita o token da sessão enquanto estiver valido; senão, renova.
token_atual = lambda: (
    st.session_state["token"]
    if token_valido(
        st.session_state["token"], st.session_state["token_expira_em"], time.time()
    )
    else renovar_token()
)

consultar = lambda token: (
    consultar_jogos(token, client_id, texto_limpo) if token else None
)

resultados = []
try:
    # Fronteira com o mundo externo (rede e disco): único try/except do app.
    # O backlog é lido do arquivo uma única vez por sessão.
    st.session_state.update(
        backlog=ler_backlog(), backlog_carregado=True
    ) if not st.session_state["backlog_carregado"] else None

    brutos = (
        consultar_com_renovacao(consultar, renovar_token, token_atual())
        if texto_limpo
        else None
    )
    resultados = list(map(traduzir_jogo, brutos)) if brutos else []
except requests.RequestException:
    st.error("Não foi possível falar com a IGDB. Verifique sua conexão.")
except ERROS_ARMAZENAMENTO:
    st.error("Não foi possível acessar o banco de dados (dados/backlog.db).")

BOTOES = (
    ("Quero jogar", "quero_jogar"),
    ("Jogando", "jogando"),
    ("Finalizado", "finalizado"),
)

adicionar = lambda jogo, status: st.session_state.update(
    backlog=(
        salvar_jogo({**jogo, "status": status, "horas_jogadas": 0.0}),
        ler_backlog(),
    )[-1]
)

mostrar_jogo = lambda jogo: (
    lambda colunas: (
        colunas[0].image(jogo["capa"], width=120),
        colunas[1].subheader(jogo["nome"]),
        colunas[1].caption(", ".join(jogo["genero"]) or "Sem gênero"),
        list(map(
            lambda botao: colunas[1].button(
                botao[0],
                key=f"{jogo['id']}-{botao[1]}",
                on_click=adicionar,
                args=(jogo, botao[1]),
            ),
            BOTOES,
        )),
    )
)(st.columns([1, 4]))

list(map(mostrar_jogo, resultados))

ABA_PARA_STATUS = {
    "Jogando": "jogando",
    "Quero jogar": "quero_jogar",
    "Finalizados": "finalizado",
}

jogos_da_aba = (
    filtrar_por_status(st.session_state["backlog"], ABA_PARA_STATUS[aba_atual])
    if aba_atual in ABA_PARA_STATUS
    else []
)

mostrar_backlog = lambda jogo: (
    lambda colunas: (
        colunas[0].image(jogo["capa"], width=100),
        colunas[1].subheader(jogo["nome"]),
        colunas[1].caption(", ".join(jogo["genero"]) or "Sem gênero"),
        colunas[1].write(f"{jogo['horas_jogadas']} h jogadas"),
    )
)(st.columns([1, 4]))

list(map(mostrar_backlog, jogos_da_aba))

st.info("Nenhum jogo nesta aba ainda.") if aba_atual in ABA_PARA_STATUS and not jogos_da_aba else None

mostrar_estatisticas = lambda r: (
    lambda colunas: (
        colunas[0].metric("Jogos no backlog", r["total_jogos"]),
        colunas[1].metric("Horas jogadas", f"{r['total_horas']:.1f} h"),
        st.subheader("Horas por status"),
        st.bar_chart(pd.Series(r["horas_por_status"])),
        st.subheader("Jogos por gênero"),
        st.bar_chart(r["contagem_por_genero"]) if r["contagem_por_genero"] else st.info("Sem gêneros para mostrar."),
    )
)(st.columns(2))

mostrar_estatisticas(resumo(st.session_state["backlog"])) if aba_atual == "Estatísticas" else None