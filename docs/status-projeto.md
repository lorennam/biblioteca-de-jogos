# Biblioteca de Jogos: status do projeto

Projeto em Python com Streamlit (interface) e API da IGDB (dados dos jogos), seguindo paradigma funcional estrito: sem `def`, sem `for` ou `while`, usando lambda, `map`, `filter`, `reduce` e expressões condicionais.

Última atualização: 14/11/2026

---

## Decisões já tomadas

- **Interface:** Streamlit (mantido em 14/11; ver "Frontend" abaixo). Para rodar no Windows: `python -m streamlit run app.py` (o comando `streamlit` direto não foi encontrado no PATH).
- **Frontend:** continuar no Streamlit. Astro foi avaliado e descartado por ora: exigiria reescrever a interface em JS/TS, criar uma API (FastAPI/Flask) entre o frontend e o Python, e foge do foco da disciplina (paradigma funcional em Python). Só vale reconsiderar se o projeto virar portfólio ou for publicado para outras pessoas; nesse caso `dominio/`, `armazenamento/` e `igdb/` seriam reaproveitados atrás de uma API.
- **Persistência:** **SQLite** em `dados/backlog.db` (substitui o JSON, decidido em 14/11). Motivos: chave primária resolve duplicatas, `UPDATE` simples para as horas, escrita mais segura que reescrever um arquivo inteiro, e o módulo é isolado do resto do app.
- **Tabela `jogos`:** `id` (INTEGER, chave primária), `nome`, `capa`, `genero` (texto JSON com a lista), `status`, `horas_jogadas` (REAL, padrão `0.0`). Sem `CHECK` no status por enquanto (a validação fica no domínio).
- **Operações do banco:** cada operação abre e fecha a própria conexão (simples e seguro com as threads do Streamlit). `salvar_jogo` faz *upsert*: jogo novo entra; jogo com mesmo `id` só troca o `status` e preserva as `horas_jogadas`.
- **Campos de cada jogo (no Python):** `id`, `nome`, `capa` (URL), `genero` (lista de até 3 gêneros), `status` (`"jogando"`, `"quero_jogar"` ou `"finalizado"`), `horas_jogadas` (float).
- **Status:** é definido pela ação do botão na interface, e não pela função de tradução. Cada resultado da busca tem três botões (Quero jogar, Jogando, Finalizado), cada um grava um status.
- **Horas jogadas:** começam em `0.0` ao adicionar; atualização por soma, criando um novo registro (imutabilidade) no Python e gravando o valor novo no banco.
- **Busca:** por texto digitado, com até 10 resultados (`limit 10`).
- **Falhas de rede e de armazenamento:** um único `try` no `app.py`, na fronteira com o mundo externo, com dois `except`: `requests.RequestException` (IGDB) e `ERROS_ARMAZENAMENTO` (tupla exportada por `backlog_sqlite.py`: `OSError`, `sqlite3.Error`, `ValueError`). Dentro das funções de rede, erros HTTP viram `None`; as funções de banco deixam o erro subir.
- **Token da Twitch (14/11):** `obter_token` devolve `{"token", "expira_em"}` (ou `None` se falhar). O vencimento é agora + `expires_in` − `MARGEM_SEGURANCA` (60 s) e fica em `st.session_state["token"]` e `st.session_state["token_expira_em"]`. A validade é checada por `token_valido(token, expira_em, agora)` (pura, recebe o "agora" como argumento, o que a torna testável); se o token estiver inválido, `token_atual` renova antes da consulta. `obter_token` também ganhou `timeout=10`.
- **Retentativa da consulta (14/11):** `consultar_com_renovacao(consultar, renovar, token)`, função pura de ordem superior. Se a consulta devolver `None` e houver token, pede um token novo uma única vez e tenta de novo. Lista vazia (`[]`) é resultado válido e não conta como falha (comparação com `is None`, não com `or`).
- **Banco inexistente ou corrompido:** inexistente → o banco e a pasta `dados/` são criados vazios ao abrir; corrompido → o erro sobe até a fronteira e o app mostra uma mensagem, sem sobrescrever nada.
- **Estados válidos:** tupla `ESTADOS_VALIDOS`, com normalização por `strip().lower()`.
- **Capa padrão:** expressão condicional, com constante `CAPA_PADRAO` apontando para `placehold.co` (substitui o `via.placeholder.com`).
- **Status inválido nas estatísticas:** `filtrar_por_status` devolve lista vazia `[]` (e não `None`), para que contagens e somas continuem funcionando.
- **Conversão de horas:** se as horas chegarem como texto (ex.: formulário), a conversão com `float(...)` é feita na entrada, antes de gravar no banco. O `estatisticas.py` sempre recebe número.
- **Credenciais:** `.streamlit/secrets.toml` com `client_id` e `client_secret` no topo do arquivo, em minúsculas e entre aspas (sem seção `[IGDB]`), lidas via `st.secrets`.
- **Estado da sessão:** `ESTADO_INICIAL` (`token`, `token_expira_em`, `backlog`, `backlog_carregado`) aplicado com `setdefault` dentro de `map`, para não apagar dados a cada rerun. O backlog é lido do banco uma única vez por sessão (controlado por `backlog_carregado`), dentro do `try` da fronteira.
- **Navegação:** tupla `ABAS` (Buscar, Jogando, Quero jogar, Finalizados, Estatísticas) na barra lateral; dicionário `ABA_PARA_STATUS` liga o nome da aba ao status guardado, sem `if` em sequência.
- **Adicionar jogo:** a função `adicionar` cria um dicionário novo (`{**jogo, "status": ..., "horas_jogadas": 0.0}`), chama `salvar_jogo` (upsert no banco) e recarrega a lista com `ler_backlog()`, de modo que a sessão sempre espelha o banco. Clicar de novo num jogo existente move o jogo de aba, sem duplicar.
- **Padrão de interface funcional:** `list(map(...))` para consumir o `map` preguiçoso; lambda que recebe `st.columns(...)` como argumento no lugar de variável intermediária; `... if condição else None` no lugar de `if` com bloco.
- **Padrão funcional para I/O:** lambdas com a "tupla com `[-1]`" para encadear efeitos e devolver o resultado, e lambdas aninhadas para guardar valores intermediários (ex.: a conexão).

## Estrutura de pastas

```
biblioteca-de-jogos/
├── app.py                  # ponto de entrada do Streamlit (só interface) — blocos 1 a 9 escritos
├── src/
│   ├── igdb/
│   │   └── cliente.py      # I/O: obter token e consultar a IGDB
│   ├── dominio/
│   │   ├── traducao.py     # funções puras: traduzir_jogo, limpar_texto_busca
│   │   └── estatisticas.py # funções puras: filtros e contagens (criado e testado)
│   └── armazenamento/
│       └── backlog_sqlite.py # I/O: ler e salvar no SQLite (criado e testado)
├── dados/
│   └── backlog.db          # dados do usuário (não versionar; criado pelo app)
├── .streamlit/
│   └── secrets.toml        # credenciais (não versionar)
├── tests/                  # testes com assert (teste.py, teste_token.py, ...)
├── .gitignore              # cobre .streamlit/, dados/ e dados/backlog.db
└── requirements.txt        # feito
```

---

## O que já foi feito

1. **Ambiente:** pasta do projeto criada, `.streamlit/secrets.toml` com `client_id` e `client_secret` da IGDB (agora lido pelo `app.py` via `st.secrets`; formato corrigido em 11/11), estrutura de pastas montada no VS Code, `.gitignore` conferido.
2. **Constantes em `cliente.py`:** `URL_TOKEN`, `URL_JOGOS`, `CABECALHO_CLIENT_ID` e `CABECALHO_AUTORIZACAO`. Endereços confirmados na documentação.
3. **`obter_token`:** lambda que faz POST para a Twitch com `grant_type=client_credentials` e devolve o `access_token`, ou `None` em caso de falha. **Testado:** o token foi obtido com sucesso. (Em 14/11 passou a devolver `{"token", "expira_em"}` e ganhou `timeout=10`; ver item 14.)
4. **`consultar_jogos`:** lambda que faz POST para a IGDB com os cabeçalhos e a consulta, e devolve a lista de jogos ou `None`. **Testado:** retornou 10 jogos com `cover.url` e `genres.name` expandidos.
5. **`montar_consulta`:** lambda pura que devolve a string Apicalypse a partir do texto limpo. Foi separada de `consultar_jogos`. **Testada** com `"Zelda"`: o texto aparece na consulta e ela tem três linhas.
6. **`limpar_texto_busca`:** remove aspas duplas e espaços das extremidades; devolve `None` para texto vazio. **Testada** com três casos: texto normal, com aspas e espaços, e só espaços (agora com `assert`, em `teste.py`). Já está em `src/dominio/traducao.py`.
7. **`traduzir_jogo`:** lambda pura, sem `status`, que converte o item bruto da IGDB para o formato interno: `https:` na capa, gêneros como texto (até 3, com `item.get("genres", [])` e `[:3]`) e `CAPA_PADRAO` quando não há capa. Versão final escrita em 11/11 para `src/dominio/traducao.py`, com cinco `assert` de teste para o `teste.py` (com capa, sem capa, sem `status`, gêneros, capa padrão). **Falta confirmar que foi colada, que os testes passaram e que a versão antiga saiu do `teste.py`.** (Indício de que funciona: em 14/11 a busca real trouxe "The Legend of Zelda" com capa e gênero `Adventure`, sem campo `status` vindo da tradução.)
8. **Fronteira de erros:** bloco `try` no `app.py` (bloco 6) com `timeout=10` em `consultar_jogos`, agora com dois `except` (rede e armazenamento). **Ainda não testada** com a internet desligada.
9. **`src/dominio/estatisticas.py`:** todas as funções escritas como lambdas, sem `def`, `for` ou `while`:
   - `normalizar_status`: `strip().lower()`.
   - `filtrar_por_status(jogos, status)`: normaliza, valida com `ESTADOS_VALIDOS` e filtra; status inválido devolve `[]`. **Testada** com `"jogando"`, `"finalizado"`, `"quero_jogar"`, `"  JOGANDO "` e `"abacaxi"`.
   - `total_de_jogos(jogos)`: tamanho da lista. **Testada.**
   - `total_de_horas(jogos)`: `reduce` com valor inicial `0.0`. **Testada** (140.0 com dados de teste, `0.0` com lista vazia).
   - `horas_por_status(jogos, status)`: composição de `filtrar_por_status` com `total_de_horas`. **Testada** com os cinco casos de status.
   - `todos_os_generos(jogos)`: concatena as listas de gêneros com `reduce`. **Testada.**
   - `contagem_por_genero(jogos)`: `reduce` com acumulador-dicionário imutável (`{**acc, g: acc.get(g, 0) + 1}`). **Testada** com dados reais de teste e, com `assert`, com um jogo de `"genero": []` sozinho (`{}`) e misturado a outro (resultado igual, sem erro).
   - `resumo(jogos)`: junta `total_jogos`, `total_horas`, `horas_por_status` (via `dict(map(...))` sobre `ESTADOS_VALIDOS`) e `contagem_por_genero`. **Testada** com dados de teste e com lista vazia.
10. **`app.py` (blocos 1 a 9):** escritos e entregues em 11/11/2026, um commit por bloco (títulos em "Interface"). Blocos 1 a 3 já rodaram e foram conferidos (título/ícone, credenciais, estado da sessão). Em 14/11, a busca real e o botão "Quero jogar" foram confirmados (o jogo apareceu no banco). Os demais comportamentos (abas, estatísticas) ainda precisam ser conferidos (ver "Testes pendentes").
11. **`src/armazenamento/backlog_sqlite.py` (14/11):** módulo todo em lambdas, sem `def`, `for`, `while`, `with` nem `try`. Contém:
    - `jogo_para_linha` e `linha_para_jogo`: puras; convertem entre o dicionário do jogo e a linha da tabela (gêneros ↔ texto JSON).
    - `conectar`, `preparar`, `abrir`: criam a pasta `dados/`, abrem a conexão e garantem que a tabela exista.
    - `ler_backlog(caminho)`: devolve a lista de jogos na ordem de inserção.
    - `salvar_jogo(jogo, caminho)`: *upsert* (insere ou troca só o status) e devolve o jogo.
    - `ERROS_ARMAZENAMENTO`: tupla para o `except` do `app.py`.
    - **Testado** em 14/11 com `assert` no `teste.py`, usando banco temporário: banco vazio, ida e volta (acentos, `[]` de gêneros), upsert preservando horas e arquivo inválido gerando erro tratável. **Verificado no app:** um jogo adicionado como "quero_jogar" apareceu no `dados/backlog.db` com os campos corretos.
12. **`app.py` ligado à persistência (14/11):** import de `backlog_sqlite`, flag `backlog_carregado`, leitura do banco dentro do `try`, `adicionar` chamando `salvar_jogo` + `ler_backlog()` e novo `except ERROS_ARMAZENAMENTO`.
13. **Verificação de `...` soltos no `app.py` (14/11):** nenhuma linha termina em `...` e o arquivo não tem a expressão `Ellipsis`; se o aviso voltar a aparecer na tela, reabrir o item.
14. **Renovação do token (14/11):** em `src/igdb/cliente.py`, todas em lambdas:
    - `calcular_expiracao(agora, expires_in, margem)`: pura; instante de renovação (agora + `expires_in` − margem).
    - `token_valido(token, expira_em, agora)`: pura; o token existe e `agora < expira_em`.
    - `montar_registro_token(dados, agora)`: pura; converte a resposta da Twitch no registro `{"token", "expira_em"}`.
    - `consultar_com_renovacao(consultar, renovar, token)`: pura (recebe as funções como argumento); renova uma única vez e repete a consulta se vier `None`.
    - `obter_token`: agora devolve o registro (ou `None`) e tem `timeout=10`.
    - No `app.py`: lambdas `renovar_token` (atualiza `token` e `token_expira_em` na sessão), `token_atual` (reaproveita se válido, senão renova) e `consultar`; o bloco 6 chama `consultar_com_renovacao(consultar, renovar_token, token_atual())`.
    - **Testado** em 14/11 (sandbox) com `tests/teste_token.py`: contas de vencimento, bordas do `token_valido` (limite exato e `0.0` inicial), `obter_token` com resposta 200/400 simulada e quatro cenários do retry (sem falha, falha e sucesso, falha sempre, sem token).

---

## O que falta fazer

### Ajustes em código já escrito

- [x] **Remover `"status": "quero_jogar"` de `traduzir_jogo`** (versão nova não tem o campo; falta só confirmar que ela substituiu a antiga).
- [x] **Mover `limpar_texto_busca`** para `src/dominio/traducao.py` (feito).
- [x] **Procurar `...` soltos no `app.py`:** conferido em 14/11, não há nenhum (ver item 13 acima).
- [ ] **Mover `traduzir_jogo`** para `src/dominio/traducao.py` e remover a versão antiga do `teste.py` (código entregue em 11/11; falta colar).
- [ ] **Remover os `print` de teste de `traducao.py`.** Eles aparecem toda vez que o módulo é importado.
- [x] **Usar `montar_consulta(texto)`** dentro de `consultar_jogos`, no lugar do f-string fixo (conferido em 14/11: já estava feito no `cliente.py`).
- [ ] **Remover o `print` do token** do `teste.py` e não compartilhar o token de novo.
- [x] **Conferir a assinatura das funções de `cliente.py`:** conferido em 14/11 com o arquivo real; `obter_token(client_id, client_secret)` e `consultar_jogos(token, client_id, texto)` batem com as chamadas do `app.py`.
- [ ] **Apagar os restos do JSON:** remover `src/armazenamento/backlog_json.py` e `dados/backlog.json`, se existirem.
- [ ] **Testar a fronteira de erros** desligando a internet.
- [ ] **Centralizar `ESTADOS_VALIDOS`:** hoje está definida em `estatisticas.py`; decidir se fica ali ou em um módulo comum, para a interface, as regras de validação e (se quiser) o `CHECK` do banco reaproveitarem a mesma tupla.
- [ ] **`todos_os_generos`:** usa `jogo["genero"] + acc` (ordem invertida). Não afeta a contagem, mas pode ser trocado por `acc + jogo["genero"]` por clareza.

### Testes pendentes

- [x] Testar `montar_consulta("Zelda")` e confirmar a estrutura de três linhas.
- [x] Testar `contagem_por_genero` com um jogo de `"genero": []`, sozinho e misturado aos outros.
- [x] Testar `backlog_sqlite.py` isoladamente (14/11, passou).
- [x] Busca real de "Zelda" no app e adicionar com "Quero jogar" (14/11: o jogo foi gravado no banco).
- [ ] Rodar `tests/teste_token.py` na máquina (passou na sandbox em 14/11); a partir da raiz: `python -m tests.teste_token`.
- [ ] Rodar os `assert` de `traduzir_jogo` no `teste.py` e testar sobre um item real da IGDB, conferindo `https:` na capa, gêneros como texto e ausência de `status`.
- [ ] **F5** na página: o jogo adicionado deve continuar na aba "Quero jogar".
- [ ] Clicar de novo no mesmo jogo: não deve duplicar.
- [ ] Clicar em "Finalizado" no mesmo jogo: ele deve sair de "Quero jogar" e aparecer em "Finalizados", sem duplicar.
- [ ] Parar e reiniciar o servidor: o jogo deve continuar lá.
- [ ] Adicionar jogos com status diferentes e conferir que cada um aparece só na aba correspondente.
- [ ] Aba "Estatísticas" com backlog vazio (sem erro) e com jogos; se `st.bar_chart` não aceitar dicionário, converter com `pd.Series(...)`.
- [ ] Banco corrompido (com o app parado, trocar o conteúdo do `backlog.db` por texto): deve aparecer a mensagem de erro, sem travar o app.

### Interface (`app.py`)

- [x] Bloco 1: configuração da página. Commit: `feat(app): configura página principal do Streamlit`.
- [x] Bloco 2: carregamento das credenciais via `st.secrets`. Commit: `feat(app): carrega credenciais da IGDB via st.secrets`.
- [x] Bloco 3: estado da sessão (token e backlog). Commit: `feat(app): inicializa estado da sessão com token e backlog`.
- [x] Bloco 4: barra lateral com navegação entre as abas. Commit: `feat(app): adiciona barra lateral com navegação entre abas`.
- [x] Bloco 5: campo de busca. Commit: `feat(app): adiciona campo de busca de jogos`.
- [x] Bloco 6: pipeline de busca (limpeza, consulta, tradução) com a fronteira de erros. Commit: `feat(app): conecta pipeline de busca com tratamento de erros`.
- [x] Bloco 7: exibição dos resultados e botão para adicionar ao backlog, com status definido pela ação do botão. Commit: `feat(app): exibe resultados com botão para adicionar ao backlog`.
- [x] Bloco 8: abas do backlog (jogando, quero jogar, finalizado). Commit: `feat(app): exibe abas do backlog por status`.
- [x] Bloco 9: estatísticas (chama `resumo(jogos)` e exibe os valores). Commit: `feat(app): exibe estatísticas do backlog`.
- [ ] Commit da persistência: `feat(armazenamento): persiste o backlog em SQLite` (módulo) e `feat(app): liga o backlog ao banco SQLite` (app).
- [ ] Commit da renovação do token: `feat(igdb): renova o token da Twitch antes do vencimento` (`cliente.py` + `app.py` + `tests/teste_token.py`).
- [ ] Passada de visual (layout e estilo) depois que tudo funcionar; ideia: trocar `t_thumb` por `t_cover_big` na URL da capa se as imagens ficarem pequenas; tema via `.streamlit/config.toml`.

### Renovação do token

- [x] Guardar também o `expires_in` e o instante de criação do token, para decidir quando renovar (`obter_token` devolve `{"token", "expira_em"}`; `token_expira_em` da sessão agora é usado).
- [x] Verificação de validade do token feita por expressão condicional (`token_valido` + `token_atual` no `app.py`).
- [x] Ao receber `None` da consulta, pedir um token novo uma única vez e tentar de novo (`consultar_com_renovacao`).
- [ ] Testar no app: buscas normais continuam funcionando e, sabotando o token da sessão (valor inválido com `token_expira_em` no futuro), a primeira consulta falha e a retentativa com token novo funciona sem o usuário perceber.

### Persistência (`src/armazenamento/backlog_sqlite.py`)

- [x] Função que lê o banco e devolve a lista de jogos (`ler_backlog`).
- [x] Função que grava no banco (`salvar_jogo`, com upsert).
- [x] Decidir como tratar banco inexistente ou corrompido (ver "Decisões").
- [x] Carregar o backlog do banco para `st.session_state` ao iniciar e gravar a cada alteração (falta só confirmar o teste do F5).
- [ ] Função para atualizar as horas de um jogo (`UPDATE jogos SET horas_jogadas = ? WHERE id = ?`), recebendo o valor já calculado por soma no Python.
- [ ] Avaliar se `salvar_jogo` deve validar o status com `ESTADOS_VALIDOS` antes de gravar.

### Regras de validação

- [x] Validar o status com `ESTADOS_VALIDOS` e normalização `strip().lower()` (feito em `filtrar_por_status`; na interface os botões são fixos, então o status já nasce válido, mas vale aplicar a validação ao adicionar um jogo).
- [x] Tratar duplicatas: resolvido pelo upsert com chave primária (código feito em 14/11; falta o teste no app).
- [ ] Atualizar horas jogadas por soma, criando um novo registro (precisa de um campo/botão na interface e da função de `UPDATE` acima; hoje `horas_jogadas` fica sempre em `0.0`).

### Melhorias futuras

- [ ] Filtrar resultados da busca para reduzir edições de fã e expansões na lista, já que a busca por aproximação pode trazer itens pouco relevantes.
- [ ] Imagem padrão local, no lugar do serviço externo `placehold.co`, que também pode sair do ar.
- [x] Mover os testes de `teste.py` para uma pasta própria (feito em 14/11: pasta `tests/` na raiz). Como os testes importam `src.*`, rodar a partir da raiz do projeto com `python -m tests.<nome>` (ex.: `python -m tests.teste_token`); `python tests/teste_token.py` não acha o `src`.
- [ ] Se o app for publicado: o disco de serviços de hospedagem costuma ser temporário e o banco seria compartilhado entre todos os visitantes; seria preciso um banco externo e separar os dados por usuário.
- [ ] Opcional: importar para o SQLite jogos de teste que estavam no antigo `backlog.json`, se houver algum que valha manter.

### Entrega do projeto

- [x] Preencher o `requirements.txt` (já criado) com `streamlit` e `requests`. (Conferir se `pandas` também está, pois o `app.py` importa.)
- [x] Conferir se `.streamlit/secrets.toml` e os dados do usuário estão no `.gitignore` antes do primeiro commit (agora `dados/backlog.db`).

---

## Próximo passo sugerido

Rodar `tests/teste_token.py` e testar a renovação do token no app, terminar os testes da persistência listados acima (F5, duplicata, mudar de status, reiniciar o servidor, estatísticas) e fazer os commits (persistência e token). Em seguida: o **botão de horas jogadas** (função de `UPDATE` no `backlog_sqlite.py` + campo na interface), fechar as pendências de `traducao.py` (colar `traduzir_jogo` e remover os `print`), testar a fronteira de erros sem internet e, por fim, a passada de visual.