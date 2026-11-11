import streamlit as st

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

# 6. Pipeline de busca: limpeza -> consulta -> tradução
...

# 7. Exibição: resultados da busca com opção de adicionar ao backlog
...

# 8. Exibição: abas do backlog (jogando, quero jogar, finalizado)
...

# 9. Estatísticas do backlog
...
