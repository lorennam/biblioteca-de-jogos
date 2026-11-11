# Biblioteca de Jogos: status do projeto

Projeto em Python com Streamlit (interface) e API da IGDB (dados dos jogos), seguindo paradigma funcional estrito: sem `def`, sem `for` ou `while`, usando lambda, `map`, `filter`, `reduce` e expressões condicionais.

Última atualização: 11/11/2026

---

## Decisões já tomadas

- **Interface:** Streamlit. Para rodar no Windows: `python -m streamlit run app.py` (o comando `streamlit` direto não foi encontrado no PATH).
- **Persistência:** arquivo JSON em `dados/backlog.json`.
- **Campos de cada jogo:** `id`, `nome`, `capa` (URL), `genero` (lista de até 3 gêneros), `status` (`"jogando"`, `"quero_jogar"` ou `"finalizado"`), `horas_jogadas` (float).
- **Status:** é definido pela ação do botão na interface, e não pela função de tradução. Cada resultado da busca tem três botões (Quero jogar, Jogando, Finalizado), cada um grava um status.
- **Horas jogadas:** começam em `0.0` ao adicionar; atualização por soma, criando um novo registro (imutabilidade).
- **Busca:** por texto digitado, com até 10 resultados (`limit 10`).
- **Falhas de rede:** um único `try/except` no `app.py`, na fronteira com o mundo externo. Dentro das funções, erros HTTP viram `None`.
- **Estados válidos:** tupla `ESTADOS_VALIDOS`, com normalização por `strip().lower()`.
- **Capa padrão:** expressão condicional, com constante `CAPA_PADRAO` apontando para `placehold.co` (substitui o `via.placeholder.com`).
- **Status inválido nas estatísticas:** `filtrar_por_status` devolve lista vazia `[]` (e não `None`), para que contagens e somas continuem funcionando.
- **Conversão de horas:** se as horas chegarem como texto (ex.: formulário), a conversão com `float(...)` é feita na entrada, antes de gravar no backlog. O `estatisticas.py` sempre recebe número.
- **Credenciais:** `.streamlit/secrets.toml` com `client_id` e `client_secret` no topo do arquivo, em minúsculas e entre aspas (sem seção `[IGDB]`), lidas via `st.secrets`.
- **Estado da sessão:** `ESTADO_INICIAL` (`token`, `token_expira_em`, `backlog`) aplicado com `setdefault` dentro de `map`, para não apagar dados a cada rerun.
- **Navegação:** tupla `ABAS` (Buscar, Jogando, Quero jogar, Finalizados, Estatísticas) na barra lateral; dicionário `ABA_PARA_STATUS` liga o nome da aba ao status guardado, sem `if` em sequência.
- **Adicionar jogo:** a função `adicionar` cria uma lista nova e um dicionário novo (`{**jogo, "status": ..., "horas_jogadas": 0.0}`), sem alterar o backlog existente.
- **Padrão de interface funcional:** `list(map(...))` para consumir o `map` preguiçoso; lambda que recebe `st.columns(...)` como argumento no lugar de variável intermediária; `... if condição else None` no lugar de `if` com bloco.

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
│       └── backlog_json.py # I/O: ler e gravar o JSON (ainda não criado)
├── dados/
│   └── backlog.json        # dados do usuário (não versionar)
├── .streamlit/
│   └── secrets.toml        # credenciais (não versionar)
├── .gitignore              # conferido: cobre .streamlit/ e dados/backlog.json
└── requirements.txt        # feito
```

---

## O que já foi feito

1. **Ambiente:** pasta do projeto criada, `.streamlit/secrets.toml` com `client_id` e `client_secret` da IGDB (agora lido pelo `app.py` via `st.secrets`; formato corrigido em 11/11), estrutura de pastas montada no VS Code, `.gitignore` conferido.
2. **Constantes em `cliente.py`:** `URL_TOKEN`, `URL_JOGOS`, `CABECALHO_CLIENT_ID` e `CABECALHO_AUTORIZACAO`. Endereços confirmados na documentação.
3. **`obter_token`:** lambda que faz POST para a Twitch com `grant_type=client_credentials` e devolve o `access_token`, ou `None` em caso de falha. **Testado:** o token foi obtido com sucesso.
4. **`consultar_jogos`:** lambda que faz POST para a IGDB com os cabeçalhos e a consulta, e devolve a lista de jogos ou `None`. **Testado:** retornou 10 jogos com `cover.url` e `genres.name` expandidos.
5. **`montar_consulta`:** lambda pura que devolve a string Apicalypse a partir do texto limpo. Foi separada de `consultar_jogos`. **Testada** com `"Zelda"`: o texto aparece na consulta e ela tem três linhas.
6. **`limpar_texto_busca`:** remove aspas duplas e espaços das extremidades; devolve `None` para texto vazio. **Testada** com três casos: texto normal, com aspas e espaços, e só espaços (agora com `assert`, em `teste.py`). Já está em `src/dominio/traducao.py`.
7. **`traduzir_jogo`:** lambda pura, sem `status`, que converte o item bruto da IGDB para o formato interno: `https:` na capa, gêneros como texto (até 3, com `item.get("genres", [])` e `[:3]`) e `CAPA_PADRAO` quando não há capa. Versão final escrita em 11/11 para `src/dominio/traducao.py`, com cinco `assert` de teste para o `teste.py` (com capa, sem capa, sem `status`, gêneros, capa padrão). **Falta confirmar que foi colada, que os testes passaram e que a versão antiga saiu do `teste.py`.**
8. **Fronteira de erros:** bloco `try/except requests.RequestException` no `app.py` (bloco 6), com `timeout=10` em `consultar_jogos`. **Ainda não testada** com a internet desligada.
9. **`src/dominio/estatisticas.py`:** todas as funções escritas como lambdas, sem `def`, `for` ou `while`:
   - `normalizar_status`: `strip().lower()`.
   - `filtrar_por_status(jogos, status)`: normaliza, valida com `ESTADOS_VALIDOS` e filtra; status inválido devolve `[]`. **Testada** com `"jogando"`, `"finalizado"`, `"quero_jogar"`, `"  JOGANDO "` e `"abacaxi"`.
   - `total_de_jogos(jogos)`: tamanho da lista. **Testada.**
   - `total_de_horas(jogos)`: `reduce` com valor inicial `0.0`. **Testada** (140.0 com dados de teste, `0.0` com lista vazia).
   - `horas_por_status(jogos, status)`: composição de `filtrar_por_status` com `total_de_horas`. **Testada** com os cinco casos de status.
   - `todos_os_generos(jogos)`: concatena as listas de gêneros com `reduce`. **Testada.**
   - `contagem_por_genero(jogos)`: `reduce` com acumulador-dicionário imutável (`{**acc, g: acc.get(g, 0) + 1}`). **Testada** com dados reais de teste e, com `assert`, com um jogo de `"genero": []` sozinho (`{}`) e misturado a outro (resultado igual, sem erro).
   - `resumo(jogos)`: junta `total_jogos`, `total_horas`, `horas_por_status` (via `dict(map(...))` sobre `ESTADOS_VALIDOS`) e `contagem_por_genero`. **Testada** com dados de teste e com lista vazia.
10. **`app.py` (blocos 1 a 9):** escritos e entregues em 11/11/2026, um commit por bloco (títulos em "Interface"). Blocos 1 a 3 já rodaram e foram conferidos (título/ícone, credenciais, estado da sessão). Blocos 4 a 9 foram passados em sequência; o resultado de cada teste ainda precisa ser confirmado.

---

## O que falta fazer

### Ajustes em código já escrito

- [x] **Remover `"status": "quero_jogar"` de `traduzir_jogo`** (versão nova não tem o campo; falta só confirmar que ela substituiu a antiga).
- [x] **Mover `limpar_texto_busca`** para `src/dominio/traducao.py` (feito).
- [ ] **Mover `traduzir_jogo`** para `src/dominio/traducao.py` e remover a versão antiga do `teste.py` (código entregue em 11/11; falta colar).
- [ ] **Remover os `print` de teste de `traducao.py`.** Eles aparecem toda vez que o módulo é importado.
- [ ] **Usar `montar_consulta(texto)`** dentro de `consultar_jogos`, no lugar do f-string fixo.
- [ ] **Remover o `print` do token** do `teste.py` e não compartilhar o token de novo.
- [ ] **Conferir a assinatura das funções de `cliente.py`:** o bloco 6 assume `obter_token(client_id, client_secret)` e `consultar_jogos(token, client_id, texto)`; ajustar as chamadas no `app.py` se forem diferentes.
- [ ] **Procurar `...` soltos no `app.py`:** apareceram seis "Ellipsis" na tela durante o teste do bloco 3.
- [ ] **Testar a fronteira de erros** desligando a internet.
- [ ] **Centralizar `ESTADOS_VALIDOS`:** hoje está definida em `estatisticas.py`; decidir se fica ali ou em um módulo comum, para a interface e as regras de validação reaproveitarem a mesma tupla.
- [ ] **`todos_os_generos`:** usa `jogo["genero"] + acc` (ordem invertida). Não afeta a contagem, mas pode ser trocado por `acc + jogo["genero"]` por clareza.

### Testes pendentes

- [ ] Rodar os `assert` de `traduzir_jogo` no `teste.py` e testar sobre um item real da IGDB (ex.: `The Legend of Zelda`), conferindo `https:` na capa, gêneros como texto e ausência de `status`.
- [x] Testar `montar_consulta("Zelda")` e confirmar a estrutura de três linhas.
- [x] Testar `contagem_por_genero` com um jogo de `"genero": []`, sozinho e misturado aos outros.
- [ ] Busca real de "Zelda" no app: cartões com capa, nome, gêneros e três botões.
- [ ] Adicionar jogos com status diferentes e conferir que cada um aparece só na aba correspondente.
- [ ] Aba "Estatísticas" com backlog vazio (sem erro) e com jogos; se `st.bar_chart` não aceitar dicionário, converter com `pd.Series(...)`.

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
- [ ] Passada de visual (layout e estilo) depois que tudo funcionar; ideia: trocar `t_thumb` por `t_cover_big` na URL da capa se as imagens ficarem pequenas.

### Renovação do token

- [ ] Guardar também o `expires_in` e o instante de criação do token, para decidir quando renovar (o campo `token_expira_em` já existe no estado da sessão, mas ainda não é usado).
- [ ] Verificação de validade do token feita por expressão condicional (hoje o bloco 6 só reaproveita o token guardado, sem checar vencimento).
- [ ] Ao receber `None` da consulta, pedir um token novo uma única vez e tentar de novo.

### Persistência (`src/armazenamento/backlog_json.py`)

- [ ] Função que lê `dados/backlog.json` e devolve a lista de jogos (lista vazia se o arquivo não existir).
- [ ] Função que grava a lista no arquivo.
- [ ] Decidir como tratar arquivo inexistente ou corrompido.
- [ ] Carregar o backlog do arquivo para `st.session_state` ao iniciar e gravar a cada alteração. Hoje o backlog vive só na sessão: recarregar a página (F5) apaga tudo.

### Regras de validação

- [x] Validar o status com `ESTADOS_VALIDOS` e normalização `strip().lower()` (feito em `filtrar_por_status`; na interface os botões são fixos, então o status já nasce válido, mas vale aplicar a validação ao adicionar um jogo).
- [ ] Atualizar horas jogadas por soma, criando um novo registro (precisa de um campo/botão na interface; hoje `horas_jogadas` fica sempre em `0.0`).
- [ ] Tratar duplicatas: clicar duas vezes no mesmo jogo adiciona dois registros iguais ao backlog.

### Melhorias futuras

- [ ] Filtrar resultados da busca para reduzir edições de fã e expansões na lista, já que a busca por aproximação pode trazer itens pouco relevantes.
- [ ] Imagem padrão local, no lugar do serviço externo `placehold.co`, que também pode sair do ar.
- [ ] Mover os testes de `teste.py` para uma pasta própria.

### Entrega do projeto

- [x] Preencher o `requirements.txt` (já criado) com `streamlit` e `requests`.
- [x] Conferir se `.streamlit/secrets.toml` e `dados/backlog.json` estão no `.gitignore` antes do primeiro commit.

---

## Próximo passo sugerido

Fechar as pendências do que acabou de ser escrito: colar o `traduzir_jogo` em `traducao.py` (e rodar os `assert`), remover os `print` e os `...` soltos, conferir as assinaturas de `cliente.py` e testar a busca real e a fronteira de erros com a internet desligada. Depois, o passo de maior impacto é a **persistência** (`backlog_json.py`), porque hoje o F5 apaga o backlog. Em seguida: botão de horas jogadas, tratamento de duplicatas, renovação do token e passada de visual.