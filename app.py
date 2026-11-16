import html as html_lib
import re
import time
from functools import reduce
from itertools import accumulate

import requests
import streamlit as st
from st_keyup import st_keyup

from src.igdb.cliente import obter_token, consultar_jogos, token_valido, consultar_com_renovacao
from src.dominio.traducao import limpar_texto_busca, traduzir_jogo
from src.dominio.estatisticas import filtrar_por_status, resumo
from src.dominio.regras import somar_horas
from src.interface.estilo import ESTILO
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
# Se mudar aqui, mudar também as classes .selo-* em src/interface/estilo.py.
COR_STATUS = {
    "quero_jogar": "#F59E0B",
    "jogando": "#3B82F6",
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

COR_PADRAO = "#8b5cf6"  # acento único do app (igual ao --destaque do CSS), usado com parcimônia

# Ícone de controle (traço), reaproveitado na marca da sidebar e nos estados vazios.
ICONE_JOGO = (
    '<svg viewBox="0 0 24 24" width="{t}" height="{t}" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<line x1="6" x2="10" y1="11" y2="11"/><line x1="8" x2="8" y1="9" y2="13"/>'
    '<line x1="15" x2="15.01" y1="12" y2="12"/><line x1="18" x2="18.01" y1="10" y2="10"/>'
    '<path d="M17.32 5H6.68a4 4 0 0 0-3.978 3.59c-.006.052-.01.101-.017.152C2.604 9.416 2 14.456 '
    '2 16a3 3 0 0 0 3 3c1 0 1.5-.5 2-1l1.414-1.414A2 2 0 0 1 9.828 16h4.344a2 2 0 0 1 1.414.586L17 '
    '18c.5.5 1 1 2 1a3 3 0 0 0 3-3c0-1.545-.604-6.584-.685-7.258-.007-.05-.011-.1-.017-.151A4 4 0 0 0 '
    '17.32 5z"/></svg>'
)

linhas = lambda itens, n: list(map(lambda i: itens[i:i + n], range(0, len(itens), n)))

esc = lambda texto: html_lib.escape(str(texto), quote=True)

texto_vazio_html = lambda titulo, texto: (
    '<div class="vazio">'
    f'<div class="vazio-icone">{ICONE_JOGO.format(t=22)}</div>'
    f'<div class="vazio-titulo">{titulo}</div>{texto}</div>'
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

capa_html = lambda url, nome: (
    f'<img class="capa" src="{esc(capa_hd(url))}" loading="lazy" alt="Capa de {esc(nome)}">'
    if url
    else f'<div class="capa capa-vazia" role="img" aria-label="Capa de {esc(nome)} indisponível"></div>'
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

# O <style> no mesmo elemento muda --anim-entrada a cada aba (entrar-0..4): como o NOME da
# animação muda, o CSS a reinicia mesmo que o Streamlit reaproveite os elementos da tela.
cabecalho_pagina = lambda aba: st.markdown(
    f"<style>:root {{ --anim-entrada: entrar-{ABAS.index(aba)}; --anim-fade: fade-{ABAS.index(aba)}; }}</style>"
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

_ = st.sidebar.markdown(
    '<div class="marca">'
    f'<div class="marca-icone">{ICONE_JOGO.format(t=20)}</div>'
    '<div><div class="marca-nome">Biblioteca de Jogos</div></div>'
    '</div>'
    '<div class="rotulo-sidebar">Navegação</div>',
    unsafe_allow_html=True,
)

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

buscar = st.cache_data(ttl=600, show_spinner=False)(
    lambda texto: consultar_com_renovacao(
        lambda token: consultar_jogos(token, client_id, texto) if token else None,
        renovar_token,
        token_atual(),
    )
)

resultados = []
try:
    if not st.session_state["backlog_carregado"]:
        _ = st.session_state.update(backlog=ler_backlog(), backlog_carregado=True)

    if texto_limpo:
        with st.spinner("Buscando na IGDB..."):
            inicio = time.perf_counter()
            brutos = buscar(texto_limpo)
            _ = buscar.clear() if brutos is None else None
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

# Feedback de conclusão: o card muda de lugar/selo e o toast confirma o que aconteceu.
avisar = lambda texto: st.toast(texto, icon=":material/check_circle:")

adicionar = lambda jogo, status: (
    st.session_state.update(
        backlog=(
            salvar_jogo({**jogo, "status": status, "horas_jogadas": 0.0}),
            ler_backlog(),
        )[-1]
    ),
    avisar(f"**{jogo['nome']}** adicionado em {STATUS_LABEL[status]}"),
)

# Muda o status de um jogo que já está no backlog, preservando as horas jogadas.
mover = lambda jogo, status: (
    st.session_state.update(
        backlog=(
            salvar_jogo({**jogo, "status": status}),
            ler_backlog(),
        )[-1]
    ),
    avisar(f"**{jogo['nome']}** movido para {STATUS_LABEL[status]}"),
)

# Soma as horas digitadas no cartão (somar_horas cria um jogo novo), grava no
# banco, recarrega a lista e zera o campo numérico daquele jogo.
somar = lambda jogo: (
    lambda horas: (
        st.session_state.update(
            backlog=(
                atualizar_horas(somar_horas(jogo, horas)),
                ler_backlog(),
            )[-1],
            **{f"horas-{jogo['id']}": 0.0},
        ),
        avisar(f"+{horas:g} h em **{jogo['nome']}**") if horas > 0 else None,
    )
)(st.session_state[f"horas-{jogo['id']}"])

# Remove o jogo do banco e recarrega a lista.
pedir_remocao = lambda jogo: st.session_state.update(**{f"rmc-{jogo['id']}": True})
cancelar_remocao = lambda jogo: st.session_state.update(**{f"rmc-{jogo['id']}": False})

remover = lambda jogo: (
    st.session_state.update(
        backlog=(remover_jogo(jogo["id"]), ler_backlog())[-1],
        **{f"rmc-{jogo['id']}": False},
    ),
    avisar(f"**{jogo['nome']}** removido da biblioteca"),
)

# Parte de baixo do menu "Opções" do cartão do backlog: somar horas e remover da biblioteca.
menu_extra = lambda menu, jogo: (
    lambda confirmando: (
        menu.divider(),
        menu.number_input("Horas a somar", min_value=0.0, step=0.5, key=f"horas-{jogo['id']}"),
        menu.button("Somar horas", key=f"somar-{jogo['id']}", on_click=somar,
                    args=(jogo,), use_container_width=True),
        (
            (
                menu.markdown(
                    f'<div class="aviso-remocao">Remover <b>{esc(jogo["nome"])}</b>? '
                    '<span>As horas jogadas também serão apagadas.</span></div>',
                    unsafe_allow_html=True,
                ),
                menu.button("Sim, remover", key=f"rm-sim-{jogo['id']}", type="primary",
                            on_click=remover, args=(jogo,), use_container_width=True),
                menu.button("Cancelar", key=f"rm-nao-{jogo['id']}",
                            on_click=cancelar_remocao, args=(jogo,), use_container_width=True),
            )
            if confirmando
            else menu.button("Remover da biblioteca", key=f"rm-{jogo['id']}",
                             on_click=pedir_remocao, args=(jogo,), use_container_width=True)
        ),
    )
)(
    st.session_state.get(f"rmc-{jogo['id']}", False),
)

mapa_status = status_por_id(st.session_state["backlog"])

# Cartão de resultado da busca: capa HD, título, pílulas em uma linha e menu de status.
cartao_resultado = lambda coluna, jogo: (
    lambda cartao: (
        cartao.markdown(capa_html(jogo["capa"], jogo["nome"]), unsafe_allow_html=True),
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
        cartao.markdown(capa_html(jogo["capa"], jogo["nome"]), unsafe_allow_html=True),
        cartao.markdown(
            bloco_info(
                jogo["nome"],
                selo_status(jogo["status"])
                + pilula(f"{jogo['horas_jogadas']:.1f} h", "pilula-suave")
                + pilulas_genero(jogo, 1),
            ),
            unsafe_allow_html=True,
        ),
        # Um único popover por cartão: mover de status, somar horas e remover ficam juntos.
        (lambda menu: (
            menu.caption("Mover para"),
            list(map(
                lambda botao: menu.button(
                    botao[0],
                    key=f"mv-{jogo['id']}-{botao[1]}",
                    on_click=mover,
                    args=(jogo, botao[1]),
                    disabled=jogo["status"] == botao[1],
                    use_container_width=True,
                ),
                BOTOES,
            )),
            menu_extra(menu, jogo),
        ))(cartao.popover(
            "Opções",
            icon=":material/tune:",
            use_container_width=True,
        )),
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

# Gráficos em HTML/CSS puro (sem JavaScript): aparecem junto com o painel, sem baixar
# nem executar o plotly.js. O valor exato de cada item fica no title (tooltip nativo).
cores_por_rotulo = lambda rotulos: list(map(
    lambda rotulo: COR_POR_ROTULO.get(rotulo, COR_PADRAO),
    rotulos,
))

valor_fmt = lambda v: f"{v:g}"

# Maior valor da série (1 se tudo for zero, para nunca dividir por zero).
pico = lambda valores: max(valores, default=0) or 1

ALTURA_COLUNA = 160  # altura em px da maior coluna

# "cor" pode ser um valor único ou uma lista com uma cor por barra.
grafico_colunas = lambda rotulos, valores, cor: (
    lambda topo, cores: (
        '<div class="graf"><div class="colunas">'
        + "".join(map(
            lambda t: (
                f'<div class="coluna" title="{esc(t[0])}: {valor_fmt(t[1])}">'
                f'<div class="coluna-valor">{valor_fmt(t[1])}</div>'
                f'<div class="coluna-barra" style="height:{max(4, round(t[1] / topo * ALTURA_COLUNA))}px;'
                f'background:{t[2]}"></div>'
                f'<div class="coluna-rotulo">{esc(t[0])}</div></div>'
            ),
            zip(rotulos, valores, cores),
        ))
        + "</div></div>"
    )
)(pico(valores), [cor] * len(valores) if isinstance(cor, str) else list(cor))

grafico_barras_h = lambda rotulos, valores, cor: (
    lambda topo: (
        '<div class="graf">'
        + "".join(map(
            lambda par: (
                f'<div class="hbarra" title="{esc(par[0])}: {valor_fmt(par[1])}">'
                f'<div class="hbarra-rotulo">{esc(par[0])}</div>'
                f'<div class="hbarra-trilho"><div class="hbarra-preenchimento" '
                f'style="width:{max(2, par[1] / topo * 100):.1f}%;background:{cor}"></div></div>'
                f'<div class="hbarra-valor">{valor_fmt(par[1])}</div></div>'
            ),
            zip(rotulos, valores),
        ))
        + "</div>"
    )
)(pico(valores))

# Rosca: conic-gradient com uma fatia por status (início/fim em % do total) e o total no centro.
grafico_rosca = lambda rotulos, valores: (
    lambda total, cores, fins: (
        '<div class="graf"><div class="rosca-area"><div class="rosca-caixa">'
        '<div class="rosca" style="background:conic-gradient('
        + ", ".join(map(
            lambda t: f"{t[0]} {t[1] / total * 100:.2f}% {t[2] / total * 100:.2f}%",
            zip(cores, [0, *fins[:-1]], fins),
        ))
        + ')"></div>'
        f'<div class="rosca-centro"><div class="rosca-total">{sum(valores)}</div>'
        '<div class="rosca-legenda">jogos</div></div></div></div>'
        '<div class="legenda">'
        + "".join(map(
            lambda t: (
                f'<span class="legenda-item"><i class="ponto" style="background:{t[0]}"></i>'
                f'{esc(t[1])} <b>{valor_fmt(t[2])}</b></span>'
            ),
            zip(cores, rotulos, valores),
        ))
        + "</div></div>"
    )
)(sum(valores) or 1, cores_por_rotulo(rotulos), list(accumulate(valores)))

mostrar_grafico = lambda html: st.markdown(html, unsafe_allow_html=True)

kpi = lambda coluna, rotulo, valor, cor=COR_PADRAO: coluna.container(border=True).markdown(
    f'<div class="kpi-rotulo" style="--kpi-cor:{cor}">{rotulo}</div>'
    f'<div class="kpi-valor">{valor}</div>',
    unsafe_allow_html=True,
)

# "Todos os jogos": só a capa; status e horas aparecem num véu com blur ao passar o mouse.
capa_tile = lambda url, nome: (
    f'<img class="tile-capa" src="{esc(capa_hd(url))}" loading="lazy" alt="Capa de {esc(nome)}">'
    if url
    else f'<div class="tile-capa tile-vazia" role="img" aria-label="Capa de {esc(nome)} indisponível"></div>'
)

tile_html = lambda jogo: (
    f'<div class="tile" tabindex="0" title="{esc(jogo["nome"])}">'
    + capa_tile(jogo["capa"], jogo["nome"])
    + '<div class="tile-veu">'
    + selo_status(jogo["status"])
    + f'<div class="tile-horas">{float(jogo["horas_jogadas"]):.1f} h</div>'
    + f'<div class="tile-nome">{esc(jogo["nome"])}</div>'
    + "</div></div>"
)

tiles_html = lambda backlog: (
    '<div class="tiles">' + "".join(map(tile_html, backlog)) + "</div>"
)

contador_html = lambda n, total: (
    f'<div class="lista-contador">{n} de {total} jogos</div>'
    if n != total
    else f'<div class="lista-contador">{total} {"jogo" if total == 1 else "jogos"} na biblioteca</div>'
)

# Filtros da lista "Todos os jogos": rótulo exibido -> valor interno.
FILTROS_STATUS = {
    "Todos": None,
    "Finalizados": "finalizado",
    "Jogando": "jogando",
    "Quero jogar": "quero_jogar",
}

# Rótulo exibido -> "decrescente?" (True = mais horas primeiro).
ORDENS_HORAS = {"Menos horas": False, "Mais horas": True}

filtrar_lista = lambda backlog, status: (
    backlog if status is None else filtrar_por_status(backlog, status)
)

ordenar_lista = lambda backlog, ordem: (
    sorted(backlog, key=lambda j: float(j["horas_jogadas"]), reverse=ORDENS_HORAS[ordem])
    if ordem
    else backlog
)

if aba_atual == "Estatísticas":
    resumo_atual = resumo(st.session_state["backlog"])
    contagens = list(map(
        lambda botao: len(filtrar_por_status(st.session_state["backlog"], botao[1])),
        BOTOES,
    ))

    kpis = (
        ("Jogos no backlog", str(resumo_atual["total_jogos"]), COR_PADRAO),
        ("Horas jogadas", f"{resumo_atual['total_horas']:.1f} h", COR_PADRAO),
        ("Jogando agora", str(contagens[1]), COR_STATUS["jogando"]),
        ("Finalizados", str(contagens[2]), COR_STATUS["finalizado"]),
    )
    _ = list(map(lambda par: kpi(par[0], *par[1]), zip(st.columns(4), kpis)))

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
                COR_PADRAO,
            ))

    if st.session_state["backlog"]:
        with st.container(border=True):
            cab_titulo, cab_contador = st.columns([3, 2])
            _ = cab_titulo.markdown("##### Todos os jogos")

            col_status, col_ordem, _folga = st.columns([3.1, 1.9, 4], vertical_alignment="center")
            escolha_status = col_status.segmented_control(
                "Status",
                list(FILTROS_STATUS),
                default="Todos",
                key="lista_filtro_status",
                label_visibility="collapsed",
            ) or "Todos"
            escolha_ordem = col_ordem.segmented_control(
                "Ordem",
                list(ORDENS_HORAS),
                default=None,
                key="lista_filtro_ordem",
                label_visibility="collapsed",
            )

            jogos_lista = ordenar_lista(
                filtrar_lista(st.session_state["backlog"], FILTROS_STATUS[escolha_status]),
                escolha_ordem,
            )

            _ = cab_contador.markdown(
                contador_html(len(jogos_lista), len(st.session_state["backlog"])),
                unsafe_allow_html=True,
            )

            if jogos_lista:
                _ = st.markdown(tiles_html(jogos_lista), unsafe_allow_html=True)
            else:
                _ = mostrar_vazio("Nenhum jogo nesse filtro", "Troque o status para ver os demais jogos.")