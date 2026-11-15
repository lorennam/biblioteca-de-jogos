# Biblioteca de Jogos: status do projeto

Projeto em Python com Streamlit (interface), API da IGDB (dados dos jogos) e SQLite (persistência), seguindo paradigma funcional estrito: sem `def`, `for` ou `while`; só `lambda`, `map`, `filter`, `reduce` e expressões condicionais.

Última atualização: 14/11/2026

---

## Como rodar

- **App (Windows):** `python -m streamlit run app.py`
- **Testes:** a partir da raiz do projeto, `python -m tests.<nome>` (ex.: `python -m tests.teste_regras`).

## Estrutura de pastas

```
biblioteca-de-jogos/
├── app.py                    # ponto de entrada do Streamlit (só interface)
├── src/
│   ├── igdb/
│   │   └── cliente.py        # I/O: token (com vencimento) e consulta à IGDB
│   ├── dominio/
│   │   ├── regras.py         # puras: ESTADOS_VALIDOS, normalizar_status, status_valido, somar_horas
│   │   ├── traducao.py       # puras: limpar_texto_busca, traduzir_jogo, CAPA_PADRAO
│   │   └── estatisticas.py   # puras: filtros, totais e contagens
│   └── armazenamento/
│       └── backlog_sqlite.py # I/O: ler, salvar, atualizar horas e remover no SQLite
├── tests/                    # teste.py, teste_token.py, teste_traducao.py,
│                             # teste_regras.py, teste_armazenamento.py
├── dados/
│   └── backlog.db            # dados do usuário 
├── .streamlit/
│   └── secrets.toml          # credenciais 
├── .gitignore
└── requirements.txt
```

---

## Decisões

### Interface
- **Visual refeito:** CSS próprio (`ESTILO`), navegação por botões na barra lateral com ícones (página atual em `st.session_state["pagina_atual"]`), cards em grade de 5 colunas, busca ao vivo com `st_keyup` (atualiza a cada 300 ms, sem Enter), filtro por gênero e ordenação (Relevância / Nome A-Z) nos resultados, KPIs, gráficos com Plotly (rosca de status, colunas de horas por status, barras de gêneros) e lista "Todos os jogos".
- **Capa em alta resolução só na exibição:** `capa_hd` troca `t_thumb` por `t_cover_big_2x` ao desenhar; o banco guarda a URL original.
- **Cards:** resultados da busca têm o menu "Adicionar" / "Alterar status"; cards do backlog têm "Mover para" (status) e "Mais opções" (somar horas e remover).
- **Navegação:** tupla `ABAS` (Buscar, Jogando, Quero jogar, Finalizados, Estatísticas); o dicionário `ABA_PARA_STATUS` liga a aba ao status, sem `if` em sequência.
- **Estado da sessão:** `ESTADO_INICIAL` (`token`, `token_expira_em`, `backlog`, `backlog_carregado`, `pagina_atual`) aplicado com `setdefault` dentro de `map`, para não apagar dados a cada rerun.
- **Credenciais:** `.streamlit/secrets.toml` com `client_id` e `client_secret` no topo do arquivo, em minúsculas e entre aspas (sem seção), lidas via `st.secrets`.
- **Padrões funcionais na interface:** `list(map(...))` para consumir o `map` preguiçoso; lambda que recebe o container/colunas como argumento no lugar de variável intermediária; `... if condição else None` no lugar de `if` com bloco. Os callbacks (`adicionar`, `mover`, `somar`, `remover`) seguem o mesmo molde: gravam no banco e recarregam a lista com `ler_backlog()`.

### Dados e persistência
- **SQLite em `dados/backlog.db`** (substituiu o JSON em 14/11): a chave primária evita duplicatas, o `UPDATE` das horas é simples e o módulo é isolado do resto do app.
- **Tabela `jogos`:** `id` (chave primária), `nome`, `capa`, `genero` (lista guardada como texto JSON), `status`, `horas_jogadas` (padrão `0.0`). Sem `CHECK` no SQL (não alteraria uma tabela já existente); a validação do status é feita em Python.
- **Operações:** `salvar_jogo` valida e normaliza o status **antes** de abrir o banco (`ValueError` se inválido) e faz *upsert* (jogo novo entra; mesmo `id` só troca o status e preserva as horas). `atualizar_horas` grava só o campo de horas. `remover_jogo` apaga pelo `id` (id inexistente não quebra). Cada operação abre e fecha a própria conexão (seguro com as threads do Streamlit).
- **Campos de um jogo no Python:** `id`, `nome`, `capa` (URL), `genero` (lista de até 3), `status` (`"jogando"`, `"quero_jogar"` ou `"finalizado"`), `horas_jogadas` (float).
- **Regras compartilhadas em `regras.py`:** `ESTADOS_VALIDOS`, `normalizar_status` (`strip().lower()`), `status_valido` (só aceita texto) e `somar_horas`. `estatisticas.py` e `backlog_sqlite.py` importam de lá. Status inválido em `filtrar_por_status` devolve `[]` (não `None`).
- **Horas jogadas:** começam em `0.0`. A atualização é por soma: `somar_horas` cria um jogo novo (imutabilidade) e `atualizar_horas` grava o valor no banco.
- **Carga do backlog:** lido do banco uma única vez por sessão (flag `backlog_carregado`), dentro do `try` da fronteira.

### IGDB e token
- **Busca:** por texto digitado, com até 10 resultados. Sem capa, usa `CAPA_PADRAO` (`placehold.co`), por expressão condicional.
- **Token:** `obter_token` devolve `{"token", "expira_em"}` (ou `None`). O vencimento é agora + `expires_in` − 60 s de folga (`MARGEM_SEGURANCA`). A validade é checada por `token_valido(token, expira_em, agora)`, pura, com o "agora" como argumento (por isso testável). Token inválido é renovado antes da consulta.
- **Retentativa:** `consultar_com_renovacao(consultar, renovar, token)`. Se a consulta devolver `None` e houver token, renova uma única vez e tenta de novo. Lista vazia (`[]`) é resultado válido, por isso a comparação é com `is None`, não com `or`.

### Erros
- **Um único `try` no `app.py`**, na fronteira com o mundo externo, com dois `except`: `requests.RequestException` (rede) e `ERROS_ARMAZENAMENTO` (`OSError`, `sqlite3.Error`, `ValueError`; tupla exportada por `backlog_sqlite.py`).
- **Dentro das funções:** as de rede transformam erro HTTP em `None`; as de banco deixam o erro subir. Os callbacks dos botões rodam fora do `try`, então um erro de banco ali aparece como o erro padrão do Streamlit.
- **Banco inexistente:** é criado vazio ao abrir. **Banco corrompido:** o app mostra uma mensagem e não grava nada por cima.

### Estilo funcional em I/O
- Efeitos encadeados com a "tupla com `[-1]`" (executa tudo da esquerda para a direita e devolve o último item).
- Lambdas aninhadas para guardar valores intermediários (ex.: a conexão com o banco).
- Funções puras recebem dados (como o "agora") em vez de lê-los do mundo externo.
- `lancar` (truque do gerador) levanta exceção dentro de lambda, que não tem `raise`.

---

## Concluído

- **`cliente.py`:** `obter_token`, `consultar_jogos` (com `montar_consulta`), `calcular_expiracao`, `token_valido`, `montar_registro_token` e `consultar_com_renovacao`; `timeout=10` nas chamadas.
- **`traducao.py`:** `limpar_texto_busca` (tira aspas e espaços; `None` para texto vazio) e `traduzir_jogo` (sem `status`; `https:` na capa; gêneros como texto, até 3; `CAPA_PADRAO` sem capa).
- **`regras.py`:** `ESTADOS_VALIDOS`, `normalizar_status`, `status_valido`, `somar_horas`.
- **`estatisticas.py`:** `filtrar_por_status`, `total_de_jogos`, `total_de_horas`, `horas_por_status`, `todos_os_generos` (ordem natural), `contagem_por_genero` e `resumo`, todas em lambdas.
- **`backlog_sqlite.py`:** `validar_jogo`, `jogo_para_linha`, `linha_para_jogo`, `conectar`, `preparar`, `abrir`, `executar`, `ler_backlog`, `salvar_jogo`, `atualizar_horas`, `remover_jogo` e `ERROS_ARMAZENAMENTO`, sem `def`, `for`, `while`, `with` nem `try`.
- **`app.py`:** busca com renovação de token, persistência no banco, cards com mudança de status, somar horas e remover, estatísticas com gráficos, visual novo.
- **Testes (todos passaram na máquina em 14/11):** `teste.py` (`limpar_texto_busca`, `montar_consulta`, `contagem_por_genero`), `teste_token.py`, `teste_traducao.py`, `teste_regras.py` (regras, `somar_horas`, estatísticas) e `teste_armazenamento.py` (ler, salvar, upsert, validação de status, horas, remover, banco corrompido).
- **Verificado no app:** busca real de "Zelda"; o jogo sobrevive ao F5 e ao reinício do servidor; clicar de novo no mesmo jogo não duplica; mudar o status move o jogo de aba. Os callbacks `somar` e `remover` foram testados com o banco real fora do Streamlit.
- **Limpeza e commits:** restos do JSON apagados; commits da persistência e da renovação do token feitos.

---

## Pendências

### Testes no app
- [x] **Abas:** adicionar jogos com status diferentes e conferir que cada um aparece só na aba do seu status.
- [x] **Horas:** em "Mais opções", somar 2.5 e depois 1 → o card mostra `3.5 h`; F5 mantém; "Estatísticas" reflete a soma.
- [x] **Remover:** o jogo some do card e da lista "Todos os jogos".
- [x] **Estatísticas:** com jogos e com o backlog vazio (dá para esvaziar usando o Remover).
- [x] **Sem internet:** com a internet desligada, digitar um nome na busca; deve aparecer a mensagem de erro da IGDB, sem quebrar o app.

### Ajustes
- [x] **`requirements.txt`:** listar `plotly` e `streamlit-keyup` (o `app.py` os importa); `pandas` não é mais importado.
- [x] **`.gitignore`:** se ainda não feito, ignorar só `.streamlit/secrets.toml` (assim um futuro `config.toml` pode ser versionado) e incluir `__pycache__/` e `*.pyc`. Conferir com `git ls-files dados .streamlit` que nada disso já foi commitado.

### Ideias futuras
- [x] **Filtrar os resultados da busca** para reduzir edições de fã e expansões, já que a busca por aproximação traz itens pouco relevantes.

---