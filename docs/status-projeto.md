# Biblioteca de Jogos: status do projeto

Projeto em Python com Streamlit (interface) e API da IGDB (dados dos jogos), seguindo paradigma funcional estrito: sem `def`, sem `for` ou `while`, usando lambda, `map`, `filter`, `reduce` e expressões condicionais.

Última atualização: 10/11/2026

---

## Decisões já tomadas

- **Interface:** Streamlit.
- **Persistência:** arquivo JSON em `dados/backlog.json`.
- **Campos de cada jogo:** `id`, `nome`, `capa` (URL), `genero` (lista de até 3 gêneros), `status` (`"jogando"`, `"quero_jogar"` ou `"finalizado"`), `horas_jogadas` (float).
- **Status:** é definido pela ação do botão na interface, e não pela função de tradução.
- **Horas jogadas:** atualização por soma, criando um novo registro (imutabilidade).
- **Busca:** por texto digitado, com até 10 resultados (`limit 10`).
- **Falhas de rede:** um único `try/except` no `app.py`, na fronteira com o mundo externo. Dentro das funções, erros HTTP viram `None`.
- **Estados válidos:** tupla `ESTADOS_VALIDOS`, com normalização por `strip().lower()`.
- **Capa padrão:** expressão condicional para imagem de "capa indisponível".
- **Status inválido nas estatísticas:** `filtrar_por_status` devolve lista vazia `[]` (e não `None`), para que contagens e somas continuem funcionando.
- **Conversão de horas:** se as horas chegarem como texto (ex.: formulário), a conversão com `float(...)` é feita na entrada, antes de gravar no backlog. O `estatisticas.py` sempre recebe número.

## Estrutura de pastas

```
biblioteca-de-jogos/
├── app.py                  # ponto de entrada do Streamlit (só interface)
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

1. **Ambiente:** pasta do projeto criada, `.streamlit/secrets.toml` com `client_id` e `client_secret` da IGDB (ainda não usado no código; as credenciais não foram expostas), estrutura de pastas montada no VS Code, `.gitignore` conferido.
2. **Constantes em `cliente.py`:** `URL_TOKEN`, `URL_JOGOS`, `CABECALHO_CLIENT_ID` e `CABECALHO_AUTORIZACAO`. Endereços confirmados na documentação.
3. **`obter_token`:** lambda que faz POST para a Twitch com `grant_type=client_credentials` e devolve o `access_token`, ou `None` em caso de falha. **Testado:** o token foi obtido com sucesso.
4. **`consultar_jogos`:** lambda que faz POST para a IGDB com os cabeçalhos e a consulta, e devolve a lista de jogos ou `None`. **Testado:** retornou 10 jogos com `cover.url` e `genres.name` expandidos.
5. **`montar_consulta`:** lambda pura que devolve a string Apicalypse a partir do texto limpo. Foi separada de `consultar_jogos`. **Testada** com `"Zelda"`: o texto aparece na consulta e ela tem três linhas.
6. **`limpar_texto_busca`:** remove aspas duplas e espaços das extremidades; devolve `None` para texto vazio. **Testada** com três casos: texto normal, com aspas e espaços, e só espaços (agora com `assert`, em `teste.py`). Já está em `src/dominio/traducao.py`.
7. **`traduzir_jogo`:** lambda que converte o item bruto da IGDB para o formato interno, com `https:` na capa, gêneros como texto (até 3) e fallback para imagem padrão. **Testada** com dois dicionários simulados (com e sem capa).
8. **Fronteira de erros:** bloco `try/except requests.RequestException` no `app.py`, com `timeout=10` em `consultar_jogos`. **Ainda não testada** com a internet desligada.
9. **`src/dominio/estatisticas.py`:** todas as funções escritas como lambdas, sem `def`, `for` ou `while`:
   - `normalizar_status`: `strip().lower()`.
   - `filtrar_por_status(jogos, status)`: normaliza, valida com `ESTADOS_VALIDOS` e filtra; status inválido devolve `[]`. **Testada** com `"jogando"`, `"finalizado"`, `"quero_jogar"`, `"  JOGANDO "` e `"abacaxi"`.
   - `total_de_jogos(jogos)`: tamanho da lista. **Testada.**
   - `total_de_horas(jogos)`: `reduce` com valor inicial `0.0`. **Testada** (140.0 com dados de teste, `0.0` com lista vazia).
   - `horas_por_status(jogos, status)`: composição de `filtrar_por_status` com `total_de_horas`. **Testada** com os cinco casos de status.
   - `todos_os_generos(jogos)`: concatena as listas de gêneros com `reduce`. **Testada.**
   - `contagem_por_genero(jogos)`: `reduce` com acumulador-dicionário imutável (`{**acc, g: acc.get(g, 0) + 1}`). **Testada** com dados reais de teste e, com `assert`, com um jogo de `"genero": []` sozinho (`{}`) e misturado a outro (resultado igual, sem erro).
   - `resumo(jogos)`: junta total de jogos, total de horas, horas por status (via `dict(map(...))` sobre `ESTADOS_VALIDOS`) e contagem por gênero. **Testada** com dados de teste e com lista vazia.

---

## O que falta fazer

### Ajustes em código já escrito

- [ ] **Remover `"status": "quero_jogar"` de `traduzir_jogo`.** O status passa a ser definido pela interface. Confirmar se já foi feito.
- [x] **Mover `limpar_texto_busca`** para `src/dominio/traducao.py` (feito).
- [ ] **Mover `traduzir_jogo`** para `src/dominio/traducao.py`. Ainda está no `teste.py`; o import falhou por isso.
- [ ] **Remover os `print` de teste de `traducao.py`.** Eles aparecem toda vez que o módulo é importado.
- [ ] **Usar `montar_consulta(texto)`** dentro de `consultar_jogos`, no lugar do f-string fixo.
- [ ] **Remover o `print` do token** do `teste.py` e não compartilhar o token de novo.
- [ ] **Testar a fronteira de erros** desligando a internet.
- [ ] **Centralizar `ESTADOS_VALIDOS`:** hoje está definida em `estatisticas.py`; decidir se fica ali ou em um módulo comum, para a interface e as regras de validação reaproveitarem a mesma tupla.

### Testes pendentes

- [ ] Testar `traduzir_jogo` sobre um item real da lista da IGDB (ex.: `The Legend of Zelda`), conferindo `https:` na capa, gêneros como texto e ausência de `status`. Só depois de mover a função para `traducao.py`.
- [x] Testar `montar_consulta("Zelda")` e confirmar a estrutura de três linhas.
- [x] Testar `contagem_por_genero` com um jogo de `"genero": []`, sozinho e misturado aos outros.

### Interface (`app.py`)

- [ ] Bloco 1: configuração da página.
- [ ] Bloco 2: carregamento das credenciais via `st.secrets`.
- [ ] Bloco 3: estado da sessão (token e backlog).
- [ ] Bloco 4: barra lateral com navegação entre as abas.
- [ ] Bloco 5: campo de busca.
- [ ] Bloco 6: pipeline de busca (limpeza, consulta, tradução) com a fronteira de erros.
- [ ] Bloco 7: exibição dos resultados e botão para adicionar ao backlog, com status definido pela ação do botão.
- [ ] Bloco 8: abas do backlog (jogando, quero jogar, finalizado).
- [ ] Bloco 9: estatísticas (basta chamar `resumo(jogos)` e exibir os valores).

### Renovação do token

- [ ] Guardar também o `expires_in` e o instante de criação do token, para decidir quando renovar.
- [ ] Guardar o token em `st.session_state`, com a verificação de validade feita por expressão condicional.
- [ ] Ao receber `None` da consulta, pedir um token novo uma única vez e tentar de novo.

### Persistência (`src/armazenamento/backlog_json.py`)

- [ ] Função que lê `dados/backlog.json` e devolve a lista de jogos (lista vazia se o arquivo não existir).
- [ ] Função que grava a lista no arquivo.
- [ ] Decidir como tratar arquivo inexistente ou corrompido.

### Regras de validação

- [x] Validar o status com `ESTADOS_VALIDOS` e normalização `strip().lower()` (feito em `filtrar_por_status`; falta aplicar também ao definir o status na interface, ao adicionar um jogo).
- [ ] Atualizar horas jogadas por soma, criando um novo registro.

### Melhorias futuras

- [ ] Filtrar resultados da busca para reduzir edições de fã e expansões na lista, já que a busca por aproximação pode trazer itens pouco relevantes.
- [ ] Imagem padrão local, no lugar do serviço externo `via.placeholder.com`, que pode sair do ar.
- [ ] Mover os testes de `teste.py` para uma pasta própria.

### Entrega do projeto

- [x] Preencher o `requirements.txt` (já criado) com `streamlit` e `requests`.
- [x] Conferir se `.streamlit/secrets.toml` e `dados/backlog.json` estão no `.gitignore` antes do primeiro commit.

---

## Próximo passo sugerido

Mover `traduzir_jogo` para `traducao.py` (removendo o `status` e os `print` de teste) e testá-la com um item real. Depois, usar `montar_consulta` dentro de `consultar_jogos`, escolher entre a **persistência** (`backlog_json.py`) e começar o bloco 1 do `app.py`.