"""Folha de estilo do app (somente dados: nenhuma função, nenhum I/O).

Princípios aplicados (SKILL.md):
- curvas próprias (--ease-out), nunca `transition: all`, nunca `ease-in`;
- animar só transform/opacity; cor e borda apenas com transição curta;
- feedback no :active (scale 0.97) e hover só em dispositivos com mouse;
- entrada a cada troca de tela: o cabeçalho da página define --anim-entrada (um nome de
  keyframes por aba), então o nome muda e a animação recomeça mesmo com o DOM reaproveitado;
- stagger curto (40 ms por coluna) e versão só-fade em reduced-motion;
- entrada de página abaixo de 300 ms (troca de aba acontece dezenas de vezes por dia);
- prefers-contrast: more com bordas e texto secundário mais fortes;
- tracking negativo em texto grande, levemente positivo em texto pequeno;
- um único vocabulário de cor para status (cards, lista e gráficos).
"""

ESTILO = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

:root {
    /* Acento único do app: nav ativo, hover/foco de botão, KPI padrão e legendas */
    --destaque: #8b5cf6;
    --destaque-claro: #a78bfa;
    --destaque-rgb: 139, 92, 246;
    --fundo: #0b0d14;
    --superficie: #141722;
    --superficie-2: #1b1f2e;
    --borda: #262b3d;
    --borda-suave: rgba(255, 255, 255, 0.08);
    --texto: #f1f3f9;
    --texto-suave: #9CA3AF;

    /* Movimento: curva forte de saída e durações curtas (< 300 ms) */
    --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
    --t-press: 140ms;
    --t-hover: 160ms;
    --t-enter: 280ms;        /* troca de aba é frequente: entrada < 300 ms */
    --atraso-pagina: 60ms;   /* o título entra primeiro, o conteúdo logo depois */
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
    font-optical-sizing: auto;
    -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--fundo); }

@keyframes fade-in { from { opacity: 0; } }
/* Um par por aba (ver cabecalho_pagina no app.py): trocar o NOME reinicia a animação */
@keyframes entrar-0 { from { opacity: 0; transform: translateY(8px); } }
@keyframes fade-0 { from { opacity: 0; } }
@keyframes entrar-1 { from { opacity: 0; transform: translateY(8px); } }
@keyframes fade-1 { from { opacity: 0; } }
@keyframes entrar-2 { from { opacity: 0; transform: translateY(8px); } }
@keyframes fade-2 { from { opacity: 0; } }
@keyframes entrar-3 { from { opacity: 0; transform: translateY(8px); } }
@keyframes fade-3 { from { opacity: 0; } }
@keyframes entrar-4 { from { opacity: 0; transform: translateY(8px); } }
@keyframes fade-4 { from { opacity: 0; } }
@keyframes surgir { from { opacity: 0; transform: scale(0.97); } }

/* Remove barra colorida do topo, menu de três pontos, botão Deploy e rodapé */
[data-testid="stDecoration"], #MainMenu, footer { display: none !important; }
[data-testid="stAppDeployButton"], .stAppDeployButton { display: none !important; }

/* Cabeçalho do Streamlit invisível: o título da página fica sempre legível */
header[data-testid="stHeader"] { background: transparent; }

/* Remove o ícone de âncora/link ao lado de todos os títulos */
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a,
.header-anchor,
[data-testid="stHeaderActionElements"] { display: none !important; }

/* Espaçamento do topo */
.block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1400px; }

/* ---------- Sidebar (região estrutural: material sólido e escuro) ---------- */
section[data-testid="stSidebar"] {
    background: #0f121b;
    border-right: 1px solid var(--borda);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }

.marca { display: flex; align-items: center; gap: 12px; padding: 0.25rem 0.25rem 1.1rem; }
.marca-icone {
    flex: 0 0 auto; width: 36px; height: 36px; border-radius: 10px;
    display: grid; place-items: center; color: var(--fundo);
    background: var(--destaque);
}
.marca-nome { font-weight: 600; font-size: 0.95rem; letter-spacing: -0.01em; color: var(--texto); line-height: 1.2; }
.marca-sub { font-size: 0.75rem; color: var(--texto-suave); line-height: 1.3; margin-top: 1px; }

.rotulo-sidebar {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.01em;
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
    border-radius: 8px;
    font-weight: 500;
    padding: 10px 14px;
    transition: transform var(--t-press) var(--ease-out),
                background-color var(--t-hover) ease,
                color var(--t-hover) ease;
}
section[data-testid="stSidebar"] .stButton button > div { justify-content: flex-start; width: 100%; }
section[data-testid="stSidebar"] .stButton button p { text-align: left; }
section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {
    background: rgba(var(--destaque-rgb), 0.14) !important;
    color: var(--texto) !important;
    font-weight: 600;
    box-shadow: inset 2px 0 0 var(--destaque) !important;  /* "você está aqui" */
}
@media (hover: hover) and (pointer: fine) {
    section[data-testid="stSidebar"] .stButton button:hover {
        background: var(--superficie-2) !important;
        color: var(--texto) !important;
    }
    section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"]:hover {
        background: rgba(var(--destaque-rgb), 0.22) !important;
    }
}

/* ---------- Cabeçalho de página (texto grande: tracking negativo, leading curto) ---------- */
.cabecalho {
    font-size: clamp(1.5rem, 1.25rem + 0.9vw, 1.9rem);
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.1;
    color: var(--texto);
    margin: 0;
    animation: var(--anim-entrada, entrar-0) var(--t-enter) var(--ease-out) backwards;
}
.subtitulo {
    color: var(--texto-suave); font-size: 0.92rem; line-height: 1.5; margin: 0.35rem 0 1.25rem;
    animation: var(--anim-entrada, entrar-0) var(--t-enter) var(--ease-out) 40ms backwards;
}
.titulo-secao { font-size: 0.95rem; font-weight: 600; color: var(--texto); margin: 0.1rem 0 0.5rem; }
[data-testid="stMain"] h5 {
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.005em;
    color: var(--texto);
    margin: 0.1rem 0 0.5rem;
    padding: 0;
}

/* ---------- Containers com borda ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    background: var(--superficie);
    border: 1px solid var(--borda-suave) !important;
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.35), 0 8px 24px rgba(0, 0, 0, 0.22);
    /* Entrada de página: transform + opacity apenas; "backwards" não segura o estado final,
       então o hover continua livre para mover o card depois */
    animation: var(--anim-entrada, entrar-0) var(--t-enter) var(--ease-out) backwards;
    animation-delay: calc(var(--atraso, 200ms) + var(--atraso-pagina));  /* painéis soltos entram por último */
}

/* Cards de jogo (o container que contém a capa): lift + brilho só com mouse.
   Painéis de estatística NÃO se mexem: dado que se lê não anima por estilo. */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa) {
    transition: transform 200ms var(--ease-out), border-color 200ms ease;
    animation-delay: calc(var(--atraso, 0ms) + var(--atraso-pagina));
}
/* Elevação num pseudo-elemento: animar opacity em vez de box-shadow. Sombra neutra,
   sem tingir de acento — a elevação por si já marca o hover. */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa)::after {
    content: "";
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    pointer-events: none;
    opacity: 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.35), 0 12px 30px rgba(0, 0, 0, 0.28);
    transition: opacity 200ms var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa):hover {
        transform: translateY(-2px);
        border-color: rgba(var(--destaque-rgb), 0.4) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa):hover::after { opacity: 1; }
}

/* Stagger por coluna (40 ms): cada coluna define --atraso e os blocos dentro herdam.
   Só decorativo, nunca bloqueia clique. */
:is([data-testid="stColumn"], [data-testid="column"]):nth-child(2) { --atraso: 40ms; }
:is([data-testid="stColumn"], [data-testid="column"]):nth-child(3) { --atraso: 80ms; }
:is([data-testid="stColumn"], [data-testid="column"]):nth-child(4) { --atraso: 120ms; }
:is([data-testid="stColumn"], [data-testid="column"]):nth-child(5) { --atraso: 160ms; }

/* Grade responsiva: 5 -> 3 -> 2 cards por linha (só linhas que têm cards) */
@media (max-width: 1200px) {
    [data-testid="stHorizontalBlock"]:has(.capa) { flex-wrap: wrap !important; }
    [data-testid="stHorizontalBlock"]:has(.capa) > :is([data-testid="stColumn"], [data-testid="column"]) {
        flex: 1 1 calc(33.333% - 1rem) !important;
        min-width: calc(33.333% - 1rem) !important;
    }
}
@media (max-width: 700px) {
    [data-testid="stHorizontalBlock"]:has(.capa) > :is([data-testid="stColumn"], [data-testid="column"]) {
        flex: 1 1 calc(50% - 1rem) !important;
        min-width: calc(50% - 1rem) !important;
    }
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
    /* contorno por dentro: separa a capa do card sem alterar o tamanho */
    outline: 1px solid rgba(255, 255, 255, 0.06);
    outline-offset: -1px;
}
.capa-vazia { border: 1px dashed var(--borda); outline: none; }

/* Ritmo vertical uniforme dentro do card de jogo: o Streamlit põe 1rem entre cada
   elemento, o que deixava o espaço entre os dois botões maior que o resto. */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa) [data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa) { padding: 6px; }

/* Título em uma linha, com reticências. As margens ficam aqui (nas minhas classes), assim o
   espaçamento não depende de como o Streamlit empilha os elementos. */
.nome-jogo {
    font-weight: 600; font-size: 0.95rem; letter-spacing: -0.005em; color: var(--texto);
    margin: 0.6rem 0 0.5rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Pílulas sempre em uma única linha (texto pequeno: tracking levemente positivo) */
.pilulas {
    display: flex; flex-wrap: nowrap; align-items: center; gap: 6px;
    margin: 0 0 0.6rem; height: 26px; overflow: hidden;
    -webkit-mask-image: linear-gradient(to right, #000 calc(100% - 14px), transparent);
    mask-image: linear-gradient(to right, #000 calc(100% - 14px), transparent);
}
.pilula, .selo { flex: 0 0 auto; line-height: 16px; }
.pilula {
    display: inline-block; padding: 2px 8px; border-radius: 999px;
    font-size: 11px; font-weight: 500; letter-spacing: 0.01em; color: #c7cbe0; white-space: nowrap;
    background: rgba(255, 255, 255, 0.06); border: 1px solid var(--borda-suave);
}
.pilula-suave { color: var(--texto-suave); background: transparent; }

/* Selos de status: UMA paleta para cards, lista e gráficos.
   Se mudar aqui, mudar também COR_STATUS em app.py. */
.selo {
    display: inline-block; padding: 2px 8px; border-radius: 999px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.01em; white-space: nowrap; border: 1px solid transparent;
}
.selo-quero_jogar { color: #F59E0B; background: rgba(245, 158, 11, 0.14); border-color: rgba(245, 158, 11, 0.4); }
.selo-jogando { color: #60A5FA; background: rgba(59, 130, 246, 0.16); border-color: rgba(59, 130, 246, 0.4); }
.selo-finalizado { color: #10B981; background: rgba(16, 185, 129, 0.14); border-color: rgba(16, 185, 129, 0.4); }
.selo-neutro { color: var(--texto-suave); background: transparent; border-color: var(--borda-suave); }

/* ---------- "Todos os jogos": grade só de capas, detalhes no hover ---------- */
.tiles {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 14px;
    max-height: 640px;
    overflow-y: auto;
    margin-top: 0.25rem;
    padding: 12px 4px;
    scrollbar-width: thin;
    scrollbar-color: var(--borda) transparent;
    -webkit-mask-image: linear-gradient(to bottom, transparent 0, #000 12px, #000 calc(100% - 12px), transparent 100%);
    mask-image: linear-gradient(to bottom, transparent 0, #000 12px, #000 calc(100% - 12px), transparent 100%);
}
.tiles::-webkit-scrollbar { width: 8px; }
.tiles::-webkit-scrollbar-track { background: transparent; }
.tiles::-webkit-scrollbar-thumb { background: var(--borda); border-radius: 999px; }

.tile {
    position: relative;
    aspect-ratio: 3 / 4;
    border-radius: 10px;
    overflow: hidden;
    background: var(--superficie-2);
    outline: 1px solid rgba(255, 255, 255, 0.06);
    outline-offset: -1px;
}
.tile-capa {
    display: block; width: 100%; height: 100%;
    object-fit: cover; object-position: center top;
    transition: transform 260ms var(--ease-out);
}
.tile-vazia { border: 1px dashed var(--borda); }

/* Véu: aparece no hover/foco com blur no que está atrás (backdrop-filter) */
.tile-veu {
    position: absolute; inset: 0;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 8px; padding: 12px; text-align: center;
    background: rgba(11, 13, 20, 0.5);
    -webkit-backdrop-filter: blur(7px);
    backdrop-filter: blur(7px);
    opacity: 0;
    transition: opacity 200ms var(--ease-out);
}
.tile-horas {
    font-size: 1.25rem; font-weight: 600; letter-spacing: -0.01em; line-height: 1.1;
    color: var(--texto); font-variant-numeric: tabular-nums;
}
.tile-nome {
    font-size: 0.75rem; line-height: 1.3; color: var(--texto-suave);
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.tile:focus-visible { outline: 2px solid rgba(var(--destaque-rgb), 0.75); outline-offset: 2px; }
.tile:focus-visible .tile-veu { opacity: 1; }
@media (hover: hover) and (pointer: fine) {
    .tile:hover .tile-veu { opacity: 1; }
    .tile:hover .tile-capa { transform: scale(1.06); }
}
/* Sem mouse (celular): sem hover, então o véu fica sempre visível, leve, só na base */
@media (hover: none) {
    .tile-veu {
        opacity: 1; inset: auto 0 0 0; padding: 8px; gap: 4px;
        -webkit-backdrop-filter: none; backdrop-filter: none;
        background: linear-gradient(to top, rgba(11, 13, 20, 0.92), transparent);
    }
    .tile-nome { display: none; }
    .tile-horas { font-size: 0.9rem; }
}
@media (prefers-reduced-motion: reduce) {
    .tile-capa { transition: none; }
    .tile:hover .tile-capa { transform: none; }
}

.lista-contador { text-align: right; color: var(--texto-suave); font-size: 0.8rem; padding-top: 0.2rem; }

/* Filtros em pílulas (st.segmented_control) */
[data-testid="stMain"] [data-testid="stButtonGroup"] { gap: 6px; flex-wrap: wrap; }
[data-testid="stMain"] [data-testid="stButtonGroup"] button {
    border-radius: 999px;
    border: 1px solid var(--borda-suave);
    background: transparent;
    color: var(--texto-suave);
    font-size: 0.8rem;
    font-weight: 500;
    min-height: 2rem;
    padding: 0.2rem 0.9rem;
    transition: transform var(--t-press) var(--ease-out),
                background-color var(--t-hover) ease,
                border-color var(--t-hover) ease,
                color var(--t-hover) ease;
}
[data-testid="stMain"] [data-testid="stButtonGroup"] button:active { transform: scale(0.97); }
[data-testid="stMain"] [data-testid="stButtonGroup"] button[data-testid*="Active"] {
    background: rgba(var(--destaque-rgb), 0.18);
    border-color: rgba(var(--destaque-rgb), 0.6);
    color: #ffffff;
}
@media (hover: hover) and (pointer: fine) {
    [data-testid="stMain"] [data-testid="stButtonGroup"] button:hover {
        border-color: rgba(var(--destaque-rgb), 0.5);
        color: var(--texto);
    }
}

/* ---------- Botões do conteúdo ---------- */
.stButton button, [data-testid="stPopover"] button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid var(--borda);
    background: var(--superficie-2);
    color: var(--texto);
    font-weight: 600;
    font-size: 0.85rem;
    transition: transform var(--t-press) var(--ease-out),
                background-color var(--t-hover) ease,
                border-color var(--t-hover) ease,
                color var(--t-hover) ease;
}
/* Todo elemento clicável confirma que ouviu o toque */
.stButton button:active, [data-testid="stPopover"] button:active { transform: scale(0.97); }
.stButton button:disabled, [data-testid="stPopover"] button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.stButton button:focus-visible, [data-testid="stPopover"] button:focus-visible {
    outline: 2px solid rgba(var(--destaque-rgb), 0.75);
    outline-offset: 2px;
}
@media (hover: hover) and (pointer: fine) {
    .stButton button:hover:not(:disabled), [data-testid="stPopover"] button:hover:not(:disabled) {
        border-color: var(--destaque);
        background: rgba(var(--destaque-rgb), 0.14);
        color: #ffffff;
    }
}

/* Botões compactos na área principal (a sidebar não é afetada) */
[data-testid="stMain"] .stButton button,
[data-testid="stMain"] [data-testid="stPopover"] button {
    min-height: 2.1rem;
    padding: 0.25rem 0.7rem;
    font-size: 0.8rem;
}
[data-testid="stMain"] [data-testid="stPopover"] { width: 100%; }

/* BOTAO DE CONFIRMAR REMOVER */
[data-testid="stMain"] .stButton button[data-testid="stBaseButton-primary"] {
    background: rgba(239, 68, 68, 0.16); border-color: rgba(239, 68, 68, 0.5); color: #fca5a5;
}
@media (hover: hover) and (pointer: fine) {
    [data-testid="stMain"] .stButton button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
        background: rgba(239, 68, 68, 0.26); border-color: #ef4444; color: #fff;
    }
}
.aviso-remocao { font-size: 0.82rem; line-height: 1.45; color: var(--texto); margin-bottom: 0.35rem; overflow: visible; }
.aviso-remocao span { color: var(--texto-suave); }
[data-testid="InputInstructions"] { display: none; }

/* Popover: nasce do botão que o abriu (origem no topo), nunca do centro */
[data-testid="stPopoverBody"] {
    background: var(--superficie);
    border: 1px solid var(--borda-suave);
    border-radius: 12px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
    animation: fade-in 140ms var(--ease-out);
    padding: 0.9rem !important;
    width: 250px;
    min-width: 0;
    max-width: 92vw;
}
/* Elementos do popover nunca encolhem (era isso que espremia o aviso de remoção por cima
   do botão); se não couber na tela, o popover rola. */
[data-testid="stPopoverBody"] { overflow-y: auto; max-height: 80vh; }
/* qualquer filho direto da coluna do popover: sem encolher, altura = conteúdo */
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] {
    max-height: none !important;
    overflow: visible !important;
}
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] > * {
    flex: 0 0 auto !important;
    height: auto !important;
    min-height: fit-content !important;
}
[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"],
[data-testid="stPopoverBody"] .aviso-remocao {
    height: auto !important;
    overflow: visible !important;
}
.aviso-remocao { display: block; padding-bottom: 0.15rem; }
/* o container do popover não pode cortar a sombra nem a borda */
[data-baseweb="popover"] { z-index: 1000; }
/* conteúdo do popover: espaçamento compacto e uniforme */
[data-testid="stPopoverBody"] > div[data-testid="stVerticalBlock"],
[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] { gap: 0.4rem; }
[data-testid="stPopoverBody"] .stButton button { justify-content: flex-start; padding: 0.4rem 0.75rem; }
/* opção já ativa (botão desabilitado): destaque em vez de "apagado" */
[data-testid="stPopoverBody"] .stButton button:disabled {
    opacity: 1;
    cursor: default;
    color: var(--destaque-claro);
    background: rgba(var(--destaque-rgb), 0.14);
    border-color: rgba(var(--destaque-rgb), 0.4);
}
[data-testid="stPopoverBody"] .stButton button:disabled::after {
    content: "atual"; margin-left: auto; font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.02em; opacity: 0.8;
}
[data-testid="stPopoverBody"] label p { font-size: 0.78rem; color: var(--texto-suave); }
[data-testid="stPopoverBody"] [data-testid="stCaptionContainer"] {
    font-size: 0.72rem; font-weight: 500; letter-spacing: 0.01em;
    color: var(--texto-suave); margin-bottom: -0.1rem;
}
[data-testid="stPopoverBody"] hr { margin: 0.35rem 0; border-color: var(--borda); }
[data-testid="stPopoverBody"] [data-testid="stNumberInput"] input { border-radius: 8px; }
[data-baseweb="popover"][data-popper-placement^="bottom"] [data-testid="stPopoverBody"] {
    transform-origin: top center; animation: surgir 160ms var(--ease-out);
}
[data-baseweb="popover"][data-popper-placement^="top"] [data-testid="stPopoverBody"] {
    transform-origin: bottom center; animation: surgir 160ms var(--ease-out);
}

/* ---------- Campo de busca e filtros ---------- */
div[data-testid="stTextInput"] input {
    border-radius: 10px; background: var(--superficie); border-color: var(--borda-suave);
}
div[data-baseweb="select"] > div {
    border-radius: 10px; background: var(--superficie); border-color: var(--borda-suave);
    transition: border-color var(--t-hover) ease, box-shadow var(--t-hover) ease;
}
div[data-baseweb="select"]:focus-within > div {
    border-color: var(--destaque);
    box-shadow: 0 0 0 3px rgba(var(--destaque-rgb), 0.22);
}
@media (hover: hover) and (pointer: fine) {
    div[data-baseweb="select"]:hover > div { border-color: rgba(var(--destaque-rgb), 0.5); }
}

/* Busca ao vivo (componente em iframe): só dá para estilizar o contêiner */
iframe[title="st_keyup.st_keyup"] { border-radius: 10px; color-scheme: dark; }

/* Alertas (ex.: erro da IGDB) combinando com os cards */
[data-testid="stAlert"] { border-radius: 12px; }

/* ---------- KPIs ---------- */
.kpi-rotulo {
    font-size: 0.78rem; font-weight: 500; letter-spacing: 0.01em;
    color: var(--texto-suave);
}
.kpi-rotulo::before {
    content: ""; display: inline-block; width: 6px; height: 6px; margin-right: 0.5rem;
    border-radius: 50%; vertical-align: middle; transform: translateY(-1px);
    background: var(--kpi-cor, var(--destaque));
}
.kpi-valor {
    font-size: clamp(1.9rem, 1.5rem + 1vw, 2.3rem);
    font-weight: 600; letter-spacing: -0.02em; line-height: 1.25;
    font-variant-numeric: tabular-nums;
    color: var(--texto); margin-top: 0.5rem;
    padding-bottom: 1.25rem;   /* respiro até a borda de baixo */
}
/* Respiro interno dos cards de KPI (só os que contêm .kpi-rotulo) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.kpi-rotulo) {
    padding: 0.9rem 1.1rem 0.5rem;
}

/* ---------- Estado vazio ---------- */
.vazio {
    display: flex; flex-direction: column; align-items: center;
    text-align: center; padding: 3.5rem 1rem; border-radius: 12px;
    border: 1px dashed var(--borda); color: var(--texto-suave); font-size: 0.9rem; line-height: 1.5;
    animation: var(--anim-entrada, entrar-0) var(--t-enter) var(--ease-out) var(--atraso-pagina) backwards;
}
.vazio-icone {
    width: 44px; height: 44px; border-radius: 12px; margin-bottom: 0.8rem;
    display: grid; place-items: center; color: var(--destaque-claro);
    background: rgba(var(--destaque-rgb), 0.1); border: 1px solid rgba(var(--destaque-rgb), 0.25);
}
.vazio-titulo { color: var(--texto); font-weight: 600; font-size: 1.05rem; letter-spacing: -0.01em; margin-bottom: 0.3rem; }

/* ---------- Gráficos em HTML/CSS (sem JS) ---------- */
.graf { min-height: 260px; display: flex; flex-direction: column; justify-content: center; }

.colunas { display: flex; align-items: flex-end; justify-content: space-around; gap: 18px; padding: 0.5rem 0.25rem 0; }
.coluna { flex: 1 1 0; max-width: 96px; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.coluna-valor { font-size: 0.85rem; font-weight: 600; color: var(--texto); font-variant-numeric: tabular-nums; }
.coluna-barra { width: 100%; border-radius: 8px 8px 4px 4px; }
.coluna-rotulo { margin-top: 4px; font-size: 0.75rem; letter-spacing: 0.01em; color: var(--texto-suave); white-space: nowrap; }

.hbarra { display: grid; grid-template-columns: minmax(64px, 30%) 1fr auto; align-items: center; gap: 12px; padding: 6px 0; }
.hbarra-rotulo { font-size: 0.8rem; color: var(--texto); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hbarra-trilho { height: 8px; border-radius: 999px; background: rgba(255, 255, 255, 0.06); overflow: hidden; }
.hbarra-preenchimento { height: 100%; border-radius: 999px; }
.hbarra-valor { font-size: 0.8rem; font-weight: 600; color: var(--texto-suave); font-variant-numeric: tabular-nums; min-width: 1.2em; text-align: right; }

.rosca-area { display: grid; place-items: center; padding: 0.5rem 0 1rem; }
.rosca-caixa { position: relative; width: 176px; aspect-ratio: 1; }
.rosca {
    width: 100%; height: 100%; border-radius: 50%;
    -webkit-mask: radial-gradient(farthest-side, transparent 63%, #000 64%);
    mask: radial-gradient(farthest-side, transparent 63%, #000 64%);
}
.rosca-centro { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; }
.rosca-total { font-size: 1.9rem; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; color: var(--texto); font-variant-numeric: tabular-nums; }
.rosca-legenda { font-size: 0.75rem; letter-spacing: 0.01em; color: var(--texto-suave); }
.legenda { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px 16px; font-size: 0.78rem; color: var(--texto-suave); }
.legenda-item { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
.legenda-item b { color: var(--texto); font-variant-numeric: tabular-nums; }
.ponto { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }

/* ---------- Movimento reduzido: só fade (sem deslocamento), ainda reiniciando por aba ---------- */
@media (prefers-reduced-motion: reduce) {
    div[data-testid="stVerticalBlockBorderWrapper"],
    .cabecalho, .subtitulo, .vazio {
        animation-name: var(--anim-fade, fade-0);
        animation-duration: 200ms;
        animation-timing-function: ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa) { transition: border-color var(--t-hover) ease; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.capa):hover { transform: none; }
    [data-testid="stPopoverBody"],
    [data-baseweb="popover"][data-popper-placement] [data-testid="stPopoverBody"] { animation: fade-in 150ms ease; }
    .stButton button:active, [data-testid="stPopover"] button:active,
    section[data-testid="stSidebar"] .stButton button:active { transform: none; }
}

/* Contraste alto: bordas e texto secundário mais definidos, sem depender de transparência */
@media (prefers-contrast: more) {
    :root {
        --borda: #4a5170;
        --borda-suave: rgba(255, 255, 255, 0.28);
        --texto-suave: #c9ceda;
    }
    .pilula, .selo { border-color: currentColor; }
}

/* Sem o "apagão" de 33% que o Streamlit aplica ao que está desatualizado durante o rerun:
   a troca de tela fica contínua em vez de piscar. (Apague esta regra para voltar ao padrão.) */
[data-stale="true"] { opacity: 1 !important; transition: none !important; }
</style>
"""