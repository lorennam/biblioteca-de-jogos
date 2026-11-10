# Biblioteca de Jogos: status do projeto

Projeto em Python com Streamlit (interface) e API da IGDB (dados dos jogos), seguindo paradigma funcional estrito: sem `def`, sem `for` ou `while`, usando lambda, `map`, `filter`, `reduce` e expressões condicionais.

Última atualização: 09/11/2026

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

## Estrutura de pastas

```
biblioteca-de-jogos/
├── app.py                  # ponto de entrada do Streamlit (só interface)
├── src/
│   ├── igdb/
│   │   └── cliente.py      # I/O: obter token e consultar a IGDB
│   ├── dominio/
│   │   ├── traducao.py     # funções puras: traduzir_jogo, limpar_texto_busca
│   │   └── estatisticas.py # funções puras: filtros e contagens (ainda não criado)
│   └── armazenamento/
│       └── backlog_json.py # I/O: ler e gravar o JSON (ainda não criado)
├── dados/
│   └── backlog.json        # dados do usuário (não versionar)
├── .streamlit/
│   └── secrets.toml        # credenciais (não versionar)
├── .gitignore              # ainda não conferido
└── requirements.txt        # ainda não criado
```

---

## O que já foi feito

1. **Ambiente:** pasta do projeto criada, `.streamlit/secrets.toml` com `client_id` e `client_secret` da IGDB, estrutura de pastas montada no VS Code.
2. **Constantes em `cliente.py`:** `URL_TOKEN`, `URL_JOGOS`, `CABECALHO_CLIENT_ID` e `CABECALHO_AUTORIZACAO`. Endereços confirmados na documentação.
3. **`obter_token`:** lambda que faz POST para a Twitch com `grant_type=client_credentials` e devolve o `access_token`, ou `None` em caso de falha. **Testado:** o token foi obtido com sucesso.
4. **`consultar_jogos`:** lambda que faz POST para a IGDB com os cabeçalhos e a consulta, e devolve a lista de jogos ou `None`. **Testado:** retornou 10 jogos com `cover.url` e `genres.name` expandidos.
5. **`montar_consulta`:** lambda pura que devolve a string Apicalypse a partir do texto limpo. Foi separada de `consultar_jogos`. **Teste sugerido, ainda sem confirmação.**
6. **`limpar_texto_busca`:** remove aspas duplas e espaços das extremidades; devolve `None` para texto vazio. **Testada** com três casos: texto normal, com aspas e espaços, e só espaços.
7. **`traduzir_jogo`:** lambda que converte o item bruto da IGDB para o formato interno, com `https:` na capa, gêneros como texto (até 3) e fallback para imagem padrão. **Testada** com dois dicionários simulados (com e sem capa).
8. **Fronteira de erros:** bloco `try/except requests.RequestException` no `app.py`, com `timeout=10` em `consultar_jogos`. **Ainda não testada** com a internet desligada.

---

## O que falta fazer

### Ajustes em código já escrito

- [ ] **Remover `"status": "quero_jogar"` de `traduzir_jogo`.** O status passa a ser definido pela interface. Confirmar se já foi feito.
- [ ] **Mover `traduzir_jogo` e `limpar_texto_busca`** para `src/dominio/traducao.py`, se ainda estiverem no `teste.py`.
- [ ] **Usar `montar_consulta(texto)`** dentro de `consultar_jogos`, no lugar do f-string fixo.
- [ ] **Remover o `print` do token** do `teste.py` e não compartilhar o token de novo.
- [ ] **Testar a fronteira de erros** desligando a internet.

### Testes pendentes

- [ ] Testar `traduzir_jogo` sobre um item real da lista da IGDB (ex.: `The Legend of Zelda`), conferindo `https:` na capa, gêneros como texto e ausência de `status`.
- [ ] Testar `montar_consulta("Zelda")` e confirmar a estrutura de três linhas.

### Interface (`app.py`)

- [ ] Bloco 1: configuração da página.
- [ ] Bloco 2: carregamento das credenciais via `st.secrets`.
- [ ] Bloco 3: estado da sessão (token e backlog).
- [ ] Bloco 4: barra lateral com navegação entre as abas.
- [ ] Bloco 5: campo de busca.
- [ ] Bloco 6: pipeline de busca (limpeza, consulta, tradução) com a fronteira de erros.
- [ ] Bloco 7: exibição dos resultados e botão para adicionar ao backlog, com status definido pela ação do botão.
- [ ] Bloco 8: abas do backlog (jogando, quero jogar, finalizado).
- [ ] Bloco 9: estatísticas.

### Renovação do token

- [ ] Guardar também o `expires_in` e o instante de criação do token, para decidir quando renovar.
- [ ] Guardar o token em `st.session_state`, com a verificação de validade feita por expressão condicional.
- [ ] Ao receber `None` da consulta, pedir um token novo uma única vez e tentar de novo.

### Persistência (`src/armazenamento/backlog_json.py`)

- [ ] Função que lê `dados/backlog.json` e devolve a lista de jogos (lista vazia se o arquivo não existir).
- [ ] Função que grava a lista no arquivo.
- [ ] Decidir como tratar arquivo inexistente ou corrompido.

### Domínio (`src/dominio/estatisticas.py`)

- [ ] Filtrar jogos por status.
- [ ] Contar jogos por gênero.
- [ ] Somar horas jogadas por status.
- [ ] Calcular total de jogos e total de horas.

### Regras de validação

- [ ] Validar o status com `ESTADOS_VALIDOS` e normalização `strip().lower()`.
- [ ] Atualizar horas jogadas por soma, criando um novo registro.

### Melhorias futuras

- [ ] Filtrar resultados da busca para reduzir edições de fã e expansões na lista, já que a busca por aproximação pode trazer itens pouco relevantes.
- [ ] Imagem padrão local, no lugar do serviço externo `via.placeholder.com`, que pode sair do ar.
- [ ] Mover os testes de `teste.py` para uma pasta própria.

### Entrega do projeto

- [ ] Criar `requirements.txt` com `streamlit` e `requests`.
- [ ] Conferir se `.streamlit/secrets.toml` e `dados/backlog.json` estão no `.gitignore` antes do primeiro commit.
- [ ] Se alguma credencial tiver sido exposta em local público ou compartilhado, gerar um novo `client_secret` no painel da Twitch.

---

## Próximo passo sugerido

Concluir os testes pendentes de `traduzir_jogo` e `montar_consulta`, aplicar os ajustes de código e então começar o bloco 1 do `app.py`.