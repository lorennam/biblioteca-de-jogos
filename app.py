import html as html_lib
import re
import time
from functools import reduce

import plotly.graph_objects as go
import requests
import streamlit as st
from st_keyup import st_keyup

from src.igdb.cliente import obter_token, consultar_jogos, token_valido, consultar_com_renovacao
from src.dominio.traducao import limpar_texto_busca, traduzir_jogo
from src.dominio.estatisticas import filtrar_por_status, resumo
from src.dominio.regras import somar_horas
from src.armazenamento.backlog_sqlite import (
    ler_backlog,
    salvar_jogo,
    atualizar_horas,
    remover_jogo,
    ERROS_ARMAZENAMENTO,
)

st.set_page_config(
    page_title="Biblioteca de Jogos",
    page_icon=":material/sports_esports:",
    layout="wide",
    initial_sidebar_state="expanded",
)

ESTILO = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --destaque: #7c5cff;
    --ciano: #22d3ee;
    --verde: #34d399;
    --fundo: #0b0d14;
    --superficie: #141722;
    --superficie-2: #1b1f2e;
    --borda: #262b3d;
    --borda-suave: rgba(255, 255, 255, 0.08);
    --texto: #f1f3f9;
    --texto-suave: #9CA3AF;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: var(--fundo); }

/* Remove barra colorida do topo, menu de três pontos, botão Deploy e rodapé */
[data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
[data-testid="stAppDeployButton"], .stAppDeployButton { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }

/* Remove o ícone de âncora/link ao lado de todos os títulos */
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a,
.header-anchor,
[data-testid="stHeaderActionElements"] { display: none !important; }

/* Espaçamento do topo */
.block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1400px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f121b;
    border-right: 1px solid var(--borda);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }

.rotulo-sidebar {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--texto-suave);
    padding: 0 0.25rem 0.75rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid var(--borda);
}

/* Botões de navegação da sidebar */
section[data-testid="stSidebar"] .stButton button {
    justify-content: flex-start !important;
    text-align: left !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: var(--texto-suave) !important;
    box-shadow: none !important;
    transform: none !important;
    border-radius: 8px;
    font-weight: 500;
    padding: 10px 14px;
    transition: background 0.15s ease, color 0.15s ease;
}
section[data-testid="stSidebar"] .stButton button > div {
    justify-content: flex-start;
    width: 100%;
}
section[data-testid="stSidebar"] .stButton button p {
    text-align: left;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: var(--superficie-2) !important;
    color: var(--texto) !important;
}
section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {
    background: rgba(124, 92, 255, 0.16) !important;
    color: var(--texto) !important;
    font-weight: 600;
}
section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"]:hover {
    background: rgba(124, 92, 255, 0.24) !important;
}

/* Cabeçalho de página */
.cabecalho { font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; color: var(--texto); margin: 0; line-height: 1.2; }
.subtitulo { color: var(--texto-suave); font-size: 0.92rem; margin: 0.25rem 0 1.25rem; }
.titulo-secao { font-size: 0.95rem; font-weight: 700; color: var(--texto); margin: 0.1rem 0 0.5rem; }
[data-testid="stMain"] h5 {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--texto);
    margin: 0.1rem 0 0.5rem;
    padding: 0;
}

/* Cards (containers com border=True) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--superficie);
    border: 1px solid var(--borda-suave) !important;
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.35), 0 8px 24px rgba(0,0,0,0.22);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-2px);
    border-color: rgba(124,92,255,0.45) !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.35), 0 12px 30px rgba(124,92,255,0.12);
}

/* Capa: 100% da largura do card, proporção 3:4 fixa, sem esticar nem achatar */
.capa {
    display: block;
    width: 100%;
    aspect-ratio: 3 / 4;
    object-fit: cover;
    object-position: center top;
    border-radius: 10px;
    background: var(--superficie-2);
}
.capa-vazia { border: 1px dashed var(--borda); }

/* Título em uma linha, com reticências */
.nome-jogo {
    font-weight: 600; font-size: 0.95rem; color: var(--texto);
    margin: 0.65rem 0 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Pílulas sempre em uma única linha */
.pilulas {
    display: flex; flex-wrap: nowrap; align-items: center; gap: 6px;
    margin: 0.45rem 0 0.7rem; height: 22px; overflow: hidden;
}
.pilula {
    display: inline-block; padding: 2px 8px; border-radius: 999px;
    font-size: 11px; font-weight: 500; color: #c7cbe0; white-space: nowrap;
    background: rgba(255,255,255,0.06); border: 1px solid var(--borda-suave);
}
.pilula-suave { color: var(--texto-suave); background: transparent; }

/* Selos de status */
.selo {
    display: inline-block; padding: 2px 8px; border-radius: 999px;
    font-size: 11px; font-weight: 600; white-space: nowrap; border: 1px solid transparent;
}
.selo-quero_jogar { color: #67e8f9; background: rgba(34,211,238,0.12); border-color: rgba(34,211,238,0.3); }
.selo-jogando { color: #b4a2ff; background: rgba(124,92,255,0.16); border-color: rgba(124,92,255,0.4); }
.selo-finalizado { color: #6ee7b7; background: rgba(52,211,153,0.12); border-color: rgba(52,211,153,0.3); }
.selo-neutro { color: var(--texto-suave); background: transparent; border-color: var(--borda-suave); }

/* Lista "Todos os jogos" */
.lista {
    max-height: 560px;
    overflow-y: auto;
    margin-top: 0.25rem;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.lista-linha {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    transition: background 0.15s ease;
}
.lista-linha:last-child { border-bottom: none; }
.lista-linha:hover { background: rgba(255,255,255,0.04); }
.lista-capa {
    flex: 0 0 42px;
    width: 42px;
    height: 56px;
    object-fit: cover;
    object-position: center top;
    border-radius: 6px;
    background: var(--superficie-2);
}
.lista-info { flex: 1 1 auto; min-width: 0; }
.lista-nome {
    font-weight: 600; font-size: 0.92rem; color: #ffffff;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lista-generos {
    margin-top: 2px; font-size: 12px; color: var(--texto-suave);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lista-status { flex: 0 0 auto; width: 96px; display: flex; justify-content: flex-start; }
.lista-horas {
    flex: 0 0 auto; width: 72px; text-align: right;
    font-variant-numeric: tabular-nums;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.85rem; font-weight: 600; color: var(--texto);
}
/* Cores exatas dos status na lista (as mesmas usadas nos gráficos) */
.lista .selo-jogando { color: #8B5CF6; background: rgba(139,92,246,0.14); border-color: rgba(139,92,246,0.4); }
.lista .selo-finalizado { color: #10B981; background: rgba(16,185,129,0.14); border-color: rgba(16,185,129,0.4); }
.lista .selo-quero_jogar { color: #F59E0B; background: rgba(245,158,11,0.14); border-color: rgba(245,158,11,0.4); }
.lista-contador { text-align: right; color: var(--texto-suave); font-size: 0.8rem; padding-top: 0.2rem; }

/* Botões do conteúdo */
.stButton button, [data-testid="stPopover"] button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid var(--borda);
    background: var(--superficie-2);
    color: var(--texto);
    font-weight: 600;
    font-size: 0.85rem;
    transition: all 0.2s ease;
}
.stButton button:hover, [data-testid="stPopover"] button:hover {
    border-color: var(--destaque);
    background: rgba(124,92,255,0.18);
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(124,92,255,0.28);
    transform: translateY(-1px);
}
.stButton button:active, [data-testid="stPopover"] button:active { transform: translateY(0); }

/* Botões compactos na área principal (a sidebar não é afetada) */
[data-testid="stMain"] .stButton button,
[data-testid="stMain"] [data-testid="stPopover"] button {
    min-height: 2.1rem;
    padding: 0.25rem 0.7rem;
    font-size: 0.8rem;
}
[data-testid="stMain"] [data-testid="stPopover"] { width: 100%; }

/* Campo de busca e filtros */
div[data-testid="stTextInput"] input {
    border-radius: 10px; background: var(--superficie); border-color: var(--borda-suave);
}
div[data-baseweb="select"] > div {
    border-radius: 10px; background: var(--superficie); border-color: var(--borda-suave);
}

/* Busca ao vivo (componente em iframe): só dá para estilizar o contêiner */
iframe[title="st_keyup.st_keyup"] { border-radius: 10px; color-scheme: dark; }

/* KPIs */
.kpi-rotulo {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--texto-suave);
}
.kpi-valor { font-size: 2.2rem; font-weight: 800; color: var(--texto); line-height: 1.15; margin-top: 0.2rem; }

/* Estado vazio */
.vazio {
    text-align: center; padding: 3.5rem 1rem; border-radius: 12px;
    border: 1px dashed var(--borda); color: var(--texto-suave); font-size: 0.9rem;
}
.vazio-titulo { color: var(--texto); font-weight: 700; font-size: 1.05rem; margin-bottom: 0.3rem; }
</style>
"""

_ = st.markdown(ESTILO, unsafe_allow_html=True)

credenciais_ok = "client_id" in st.secrets and "client_secret" in st.secrets

if not credenciais_ok:
    _ = st.error("Credenciais da IGDB não encontradas em .streamlit/secrets.toml")
    st.stop()

client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]

ESTADO_INICIAL = {
    "token": None,
    "token_expira_em": 0.0,
    "backlog": [],
    "backlog_carregado": False,
    "pagina_atual": "Buscar",
}

_ = list(map(lambda par: st.session_state.setdefault(par[0], par[1]), ESTADO_INICIAL.items()))

ABAS = ("Buscar", "Jogando", "Quero jogar", "Finalizados", "Estatísticas")

ICONES = {
    "Buscar": ":material/search:",
    "Jogando": ":material/sports_esports:",
    "Quero jogar": ":material/bookmark:",
    "Finalizados": ":material/emoji_events:",
    "Estatísticas": ":material/bar_chart:",
}

TITULOS = {
    "Buscar": "Buscar jogos",
    "Jogando": "Jogando agora",
    "Quero jogar": "Quero jogar",
    "Finalizados": "Finalizados",
    "Estatísticas": "Estatísticas",
}

SUBTITULOS = {
    "Buscar": "Pesquise na IGDB e adicione jogos à sua biblioteca.",
    "Jogando": "Os jogos que você está jogando neste momento.",
    "Quero jogar": "Sua fila de jogos para começar em breve.",
    "Finalizados": "Tudo o que você já terminou.",
    "Estatísticas": "Um resumo do seu backlog em números.",
}

STATUS_LABEL = {
    "quero_jogar": "Quero jogar",
    "jogando": "Jogando",
    "finalizado": "Finalizado",
}

# Cor fixa de cada status, usada nos gráficos (mesmas cores das pílulas da lista).
COR_STATUS = {
    "quero_jogar": "#F59E0B",
    "jogando": "#8B5CF6",
    "finalizado": "#10B981",
}

# Mesmo mapa, indexado pelo nome exibido do status.
COR_POR_ROTULO = dict(map(
    lambda par: (STATUS_LABEL[par[0]], par[1]),
    COR_STATUS.items(),
))

BOTOES = (
    ("Quero jogar", "quero_jogar"),
    ("Jogando", "jogando"),
    ("Finalizado", "finalizado"),
)

ABA_PARA_STATUS = {
    "Jogando": "jogando",
    "Quero jogar": "quero_jogar",
    "Finalizados": "finalizado",
}

TODOS_GENEROS = "Todos os gêneros"

COLUNAS_GRADE = 5

COR_PADRAO = "#7c5cff"

linhas = lambda itens, n: list(map(lambda i: itens[i:i + n], range(0, len(itens), n)))

esc = lambda texto: html_lib.escape(str(texto), quote=True)

texto_vazio_html = lambda titulo, texto: (
    f'<div class="vazio"><div class="vazio-titulo">{titulo}</div>{texto}</div>'
)

mostrar_vazio = lambda titulo, texto: st.markdown(
    texto_vazio_html(titulo, texto), unsafe_allow_html=True
)

titulo_secao = lambda texto: st.markdown(f"##### {texto}")

# Troca o tamanho da imagem da IGDB (miniatura) por capa em alta resolução
# na hora de exibir; o valor salvo no banco não é alterado.
capa_hd = lambda url: re.sub(
    r"t_(thumb|micro|cover_small|cover_big|logo_med|screenshot_med)(?!_2x)",
    "t_cover_big_2x",
    f"https:{url}" if url.startswith("//") else url,
)

capa_html = lambda url: (
    f'<img class="capa" src="{esc(capa_hd(url))}" loading="lazy" alt="Capa do jogo">'
    if url
    else '<div class="capa capa-vazia"></div>'
)

pilula = lambda texto, classe="": f'<span class="pilula {classe}">{esc(texto)}</span>'

pilulas_genero = lambda jogo, limite: (
    "".join(map(pilula, jogo["genero"][:limite])) or pilula("Sem gênero", "pilula-suave")
)

selo_status = lambda status: (
    f'<span class="selo selo-{status}">{STATUS_LABEL[status]}</span>'
    if status
    else '<span class="selo selo-neutro">Fora do backlog</span>'
)

bloco_info = lambda nome, pilulas: (
    f'<div class="nome-jogo" title="{esc(nome)}">{esc(nome)}</div>'
    f'<div class="pilulas">{pilulas}</div>'
)

cabecalho_pagina = lambda aba: st.markdown(
    f'<div class="cabecalho">{TITULOS[aba]}</div>'
    f'<div class="subtitulo">{SUBTITULOS[aba]}</div>',
    unsafe_allow_html=True,
)

status_por_id = lambda backlog: dict(map(lambda j: (j["id"], j["status"]), backlog))

horas_por_status_legivel = lambda r: dict(map(
    lambda par: (STATUS_LABEL.get(par[0], par[0]), par[1]),
    r["horas_por_status"].items(),
))

# Navegação: botões reais controlados por st.session_state.pagina_atual
ir_para = lambda aba: st.session_state.update(pagina_atual=aba)

_ = st.sidebar.markdown('<div class="rotulo-sidebar">Navegação</div>', unsafe_allow_html=True)

desenhar_item_menu = lambda aba: st.sidebar.button(
    aba,
    key=f"nav_{aba}",
    icon=ICONES[aba],
    type="primary" if st.session_state["pagina_atual"] == aba else "tertiary",
    use_container_width=True,
    on_click=ir_para,
    args=(aba,),
)

_ = list(map(desenhar_item_menu, ABAS))

aba_atual = st.session_state["pagina_atual"]

_ = cabecalho_pagina(aba_atual)

# Linha de busca e filtros (os filtros são preenchidos depois da consulta).
colunas_busca = st.columns([3, 1.3, 1.3]) if aba_atual == "Buscar" else None

# Busca ao vivo: devolve o texto a cada pausa de 300 ms na digitação, sem Enter.
with (colunas_busca[0] if colunas_busca else st.empty()):
    texto_busca = (
        st_keyup(
            "Buscar jogo",
            debounce=300,
            placeholder="Digite o nome do jogo, ex.: Zelda, Hollow Knight",
            label_visibility="collapsed",
            key="busca_ao_vivo",
        )
        if colunas_busca
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
    if not st.session_state["backlog_carregado"]:
        _ = st.session_state.update(backlog=ler_backlog(), backlog_carregado=True)

    if texto_limpo:
        with st.spinner("Buscando na IGDB..."):
            brutos = consultar_com_renovacao(consultar, renovar_token, token_atual())
    else:
        brutos = None

    resultados = list(map(traduzir_jogo, brutos)) if brutos else []
except requests.RequestException:
    _ = st.error("Não foi possível falar com a IGDB. Verifique sua conexão.")
except ERROS_ARMAZENAMENTO:
    _ = st.error("Não foi possível acessar o banco de dados (dados/backlog.db).")

generos_disponiveis = sorted(reduce(lambda acc, j: acc | set(j["genero"]), resultados, set()))

filtro_genero = (
    colunas_busca[1].selectbox(
        "Gênero",
        [TODOS_GENEROS, *generos_disponiveis],
        key="filtro_genero",
        label_visibility="collapsed",
    )
    if colunas_busca
    else TODOS_GENEROS
)

ordem_busca = (
    colunas_busca[2].selectbox(
        "Ordenar",
        ["Relevância", "Nome (A-Z)"],
        key="ordem_busca",
        label_visibility="collapsed",
    )
    if colunas_busca
    else "Relevância"
)

resultados_filtrados = (
    lambda lista: sorted(lista, key=lambda j: j["nome"].lower())
    if ordem_busca == "Nome (A-Z)"
    else lista
)(list(filter(
    lambda j: filtro_genero == TODOS_GENEROS or filtro_genero in j["genero"],
    resultados,
)))

adicionar = lambda jogo, status: st.session_state.update(
    backlog=(
        salvar_jogo({**jogo, "status": status, "horas_jogadas": 0.0}),
        ler_backlog(),
    )[-1]
)

# Muda o status de um jogo que já está no backlog, preservando as horas jogadas.
mover = lambda jogo, status: st.session_state.update(
    backlog=(
        salvar_jogo({**jogo, "status": status}),
        ler_backlog(),
    )[-1]
)

# Soma as horas digitadas no cartão (somar_horas cria um jogo novo), grava no
# banco, recarrega a lista e zera o campo numérico daquele jogo.
somar = lambda jogo: st.session_state.update(
    backlog=(
        atualizar_horas(somar_horas(jogo, st.session_state[f"horas-{jogo['id']}"])),
        ler_backlog(),
    )[-1],
    **{f"horas-{jogo['id']}": 0.0},
)

# Remove o jogo do banco e recarrega a lista.
remover = lambda jogo: st.session_state.update(
    backlog=(remover_jogo(jogo["id"]), ler_backlog())[-1]
)

# Menu "Mais opções" do cartão do backlog: somar horas e remover da biblioteca.
menu_extra = lambda cartao, jogo: (
    lambda menu: (
        menu.number_input(
            "Horas a somar",
            min_value=0.0,
            step=0.5,
            key=f"horas-{jogo['id']}",
        ),
        menu.button(
            "Somar horas",
            key=f"somar-{jogo['id']}",
            on_click=somar,
            args=(jogo,),
            use_container_width=True,
        ),
        menu.button(
            "Remover da biblioteca",
            key=f"rm-{jogo['id']}",
            on_click=remover,
            args=(jogo,),
            use_container_width=True,
        ),
    )
)(cartao.popover(
    "Mais opções",
    icon=":material/more_horiz:",
    use_container_width=True,
))

mapa_status = status_por_id(st.session_state["backlog"])

# Cartão de resultado da busca: capa HD, título, pílulas em uma linha e menu de status.
cartao_resultado = lambda coluna, jogo: (
    lambda cartao: (
        cartao.markdown(capa_html(jogo["capa"]), unsafe_allow_html=True),
        cartao.markdown(
            bloco_info(
                jogo["nome"],
                selo_status(mapa_status.get(jogo["id"])) + pilulas_genero(jogo, 1),
            ),
            unsafe_allow_html=True,
        ),
        (lambda menu: list(map(
            lambda botao: menu.button(
                botao[0],
                key=f"add-{jogo['id']}-{botao[1]}",
                on_click=adicionar,
                args=(jogo, botao[1]),
                disabled=mapa_status.get(jogo["id"]) == botao[1],
                use_container_width=True,
            ),
            BOTOES,
        )))(cartao.popover(
            "Alterar status" if jogo["id"] in mapa_status else "Adicionar",
            icon=":material/swap_horiz:" if jogo["id"] in mapa_status else ":material/add:",
            use_container_width=True,
        )),
    )
)(coluna.container(border=True))

# Cartão do backlog: capa HD, título, status + horas + gênero em uma linha, e botão na base.
cartao_backlog = lambda coluna, jogo: (
    lambda cartao: (
        cartao.markdown(capa_html(jogo["capa"]), unsafe_allow_html=True),
        cartao.markdown(
            bloco_info(
                jogo["nome"],
                selo_status(jogo["status"])
                + pilula(f"{jogo['horas_jogadas']:.1f} h", "pilula-suave")
                + pilulas_genero(jogo, 1),
            ),
            unsafe_allow_html=True,
        ),
        (lambda menu: list(map(
            lambda botao: menu.button(
                botao[0],
                key=f"mv-{jogo['id']}-{botao[1]}",
                on_click=mover,
                args=(jogo, botao[1]),
                disabled=jogo["status"] == botao[1],
                use_container_width=True,
            ),
            BOTOES,
        )))(cartao.popover(
            "Mover para",
            icon=":material/swap_horiz:",
            use_container_width=True,
        )),
        menu_extra(cartao, jogo),
    )
)(coluna.container(border=True))

# Distribui os itens em grade de COLUNAS_GRADE colunas, uma linha por vez.
mostrar_grade = lambda itens, desenhar: list(map(
    lambda linha: list(map(
        lambda par: desenhar(par[0], par[1]),
        zip(st.columns(COLUNAS_GRADE), linha),
    )),
    linhas(itens, COLUNAS_GRADE),
))

if aba_atual == "Buscar":
    if resultados_filtrados:
        _ = st.caption(f"{len(resultados_filtrados)} resultado(s) encontrado(s)")
        _ = mostrar_grade(resultados_filtrados, cartao_resultado)
    elif resultados:
        _ = mostrar_vazio("Nenhum jogo com esse filtro", "Troque o gênero para ver os demais resultados.")
    elif texto_limpo:
        _ = mostrar_vazio("Nada encontrado", "Tente outro nome ou uma grafia diferente.")
    else:
        _ = mostrar_vazio("Comece sua busca", "Digite o nome de um jogo na barra acima para pesquisar na IGDB.")

jogos_da_aba = (
    filtrar_por_status(st.session_state["backlog"], ABA_PARA_STATUS[aba_atual])
    if aba_atual in ABA_PARA_STATUS
    else []
)

if aba_atual in ABA_PARA_STATUS:
    if jogos_da_aba:
        _ = st.caption(f"{len(jogos_da_aba)} jogo(s) nesta lista")
        _ = mostrar_grade(jogos_da_aba, cartao_backlog)
    else:
        _ = mostrar_vazio("Nenhum jogo aqui ainda", "Use a aba Buscar para adicionar jogos a esta lista.")

# Estilo comum dos gráficos: fundo transparente, sem grade, cores da paleta.
LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#9CA3AF", size=12),
    margin=dict(l=0, r=0, t=8, b=0),
    height=300,
    showlegend=False,
)

EIXO = dict(showgrid=False, zeroline=False, showline=False)

CONFIG_GRAFICO = {"displayModeBar": False}

# Cor de cada rótulo de status, sempre pelo nome (nunca pela ordem dos dados).
cores_por_rotulo = lambda rotulos: list(map(
    lambda rotulo: COR_POR_ROTULO.get(rotulo, COR_PADRAO),
    rotulos,
))

# "cor" pode ser um valor único ou uma lista com uma cor por barra.
grafico_colunas = lambda rotulos, valores, cor: go.Figure(
    go.Bar(
        x=rotulos,
        y=valores,
        marker_color=cor,
        text=list(map(lambda v: f"{v:g}", valores)),
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}: %{y}<extra></extra>",
    )
).update_layout(**LAYOUT_BASE, xaxis=EIXO, yaxis={**EIXO, "showticklabels": False})

grafico_barras_h = lambda rotulos, valores, cor: go.Figure(
    go.Bar(
        x=valores,
        y=rotulos,
        orientation="h",
        marker_color=cor,
        text=list(map(lambda v: f"{v:g}", valores)),
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x}<extra></extra>",
    )
).update_layout(
    **LAYOUT_BASE,
    xaxis={**EIXO, "showticklabels": False},
    yaxis={**EIXO, "autorange": "reversed"},
)

grafico_rosca = lambda rotulos, valores: go.Figure(
    go.Pie(
        labels=rotulos,
        values=valores,
        hole=0.62,
        sort=False,
        textinfo="value",
        marker=dict(colors=cores_por_rotulo(rotulos), line=dict(color="#141722", width=2)),
    )
).update_layout(
    **{**LAYOUT_BASE, "showlegend": True},
    legend=dict(orientation="h", y=-0.05, font=dict(color="#9CA3AF")),
)

mostrar_grafico = lambda figura: st.plotly_chart(
    figura, use_container_width=True, theme=None, config=CONFIG_GRAFICO
)

kpi = lambda coluna, rotulo, valor: coluna.container(border=True).markdown(
    f'<div class="kpi-rotulo">{rotulo}</div><div class="kpi-valor">{valor}</div>',
    unsafe_allow_html=True,
)

# Linha da lista "Todos os jogos": capa, nome + gêneros, status e horas.
capa_lista = lambda url: (
    f'<img class="lista-capa" src="{esc(capa_hd(url))}" loading="lazy" alt="Capa do jogo">'
    if url
    else '<div class="lista-capa capa-vazia"></div>'
)

generos_lista = lambda jogo: (
    " &bull; ".join(map(esc, jogo["genero"][:3])) or "Sem gênero"
)

linha_lista = lambda jogo: (
    '<div class="lista-linha">'
    + capa_lista(jogo["capa"])
    + '<div class="lista-info">'
    + f'<div class="lista-nome" title="{esc(jogo["nome"])}">{esc(jogo["nome"])}</div>'
    + f'<div class="lista-generos">{generos_lista(jogo)}</div>'
    + "</div>"
    + f'<div class="lista-status">{selo_status(jogo["status"])}</div>'
    + f'<div class="lista-horas">{float(jogo["horas_jogadas"]):.1f} h</div>'
    + "</div>"
)

lista_html = lambda backlog: (
    '<div class="lista">' + "".join(map(linha_lista, backlog)) + "</div>"
)

contador_html = lambda n: (
    f'<div class="lista-contador">{n} jogo na biblioteca</div>'
    if n == 1
    else f'<div class="lista-contador">{n} jogos na biblioteca</div>'
)

if aba_atual == "Estatísticas":
    resumo_atual = resumo(st.session_state["backlog"])
    contagens = list(map(
        lambda botao: len(filtrar_por_status(st.session_state["backlog"], botao[1])),
        BOTOES,
    ))

    kpis = (
        ("Jogos no backlog", str(resumo_atual["total_jogos"])),
        ("Horas jogadas", f"{resumo_atual['total_horas']:.1f} h"),
        ("Jogando agora", str(contagens[1])),
        ("Finalizados", str(contagens[2])),
    )
    _ = list(map(lambda par: kpi(par[0], par[1][0], par[1][1]), zip(st.columns(4), kpis)))

    col_a, col_b, col_c = st.columns(3)

    with col_a.container(border=True):
        _ = titulo_secao("Distribuição por status")
        if sum(contagens) == 0:
            _ = st.caption("Sem dados ainda.")
        else:
            _ = mostrar_grafico(grafico_rosca(list(map(lambda b: b[0], BOTOES)), contagens))

    with col_b.container(border=True):
        _ = titulo_secao("Horas por status")
        horas_legivel = horas_por_status_legivel(resumo_atual)
        if not horas_legivel:
            _ = st.caption("Sem dados ainda.")
        else:
            _ = mostrar_grafico(grafico_colunas(
                list(horas_legivel.keys()),
                list(horas_legivel.values()),
                cores_por_rotulo(horas_legivel.keys()),
            ))

    with col_c.container(border=True):
        _ = titulo_secao("Jogos por gênero")
        itens_genero = sorted(resumo_atual["contagem_por_genero"].items(), key=lambda par: -par[1])[:8]
        if not itens_genero:
            _ = st.caption("Sem gêneros para mostrar.")
        else:
            _ = mostrar_grafico(grafico_barras_h(
                list(map(lambda par: par[0], itens_genero)),
                list(map(lambda par: par[1], itens_genero)),
                "#22d3ee",
            ))

    if st.session_state["backlog"]:
        with st.container(border=True):
            cab_titulo, cab_contador = st.columns([3, 2])
            _ = cab_titulo.markdown("##### Todos os jogos")
            _ = cab_contador.markdown(
                contador_html(len(st.session_state["backlog"])),
                unsafe_allow_html=True,
            )
            _ = st.markdown(lista_html(st.session_state["backlog"]), unsafe_allow_html=True)