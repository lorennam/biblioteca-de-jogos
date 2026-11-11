import streamlit as st
import requests
import pandas as pd
from src.igdb.cliente import obter_token, consultar_jogos
from src.dominio.traducao import limpar_texto_busca, traduzir_jogo
from src.dominio.estatisticas import filtrar_por_status, resumo

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

resultados = []
try:
    token = (
        (st.session_state["token"] or obter_token(client_id, client_secret))
        if texto_limpo
        else None
    )
    st.session_state["token"] = token or st.session_state["token"]
    brutos = consultar_jogos(token, client_id, texto_limpo) if token else None
    resultados = list(map(traduzir_jogo, brutos)) if brutos else []
except requests.RequestException:
    st.error("Não foi possível falar com a IGDB. Verifique sua conexão.")

BOTOES = (
    ("Quero jogar", "quero_jogar"),
    ("Jogando", "jogando"),
    ("Finalizado", "finalizado"),
)

adicionar = lambda jogo, status: st.session_state.update(
    backlog=st.session_state["backlog"] + [{**jogo, "status": status, "horas_jogadas": 0.0}]
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