<h1 align="center">
  Biblioteca de Jogos
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/IGDB_API-9147FF?style=for-the-badge&logo=twitch&logoColor=white" alt="IGDB" />
</p>

## Visão Geral
A Biblioteca de Jogos é uma aplicação web para organizar o backlog de jogos em um lugar só. O sistema permite pesquisar qualquer jogo na base da IGDB, adicioná-lo à biblioteca pessoal, acompanhar o status de cada título (Quero jogar, Jogando, Finalizado), registrar as horas jogadas e enxergar tudo em números por meio de um painel de estatísticas.

O projeto foi desenvolvido com foco em um **paradigma funcional estrito**: o código não usa `def`, `for` nem `while`, apenas `lambda`, `map`, `filter`, `reduce` e expressões condicionais. A lógica de negócio é feita de funções puras, e o acesso ao mundo externo (rede e banco de dados) fica isolado em módulos próprios, o que torna cada parte fácil de testar e de raciocinar.

## Equipe

- [Lorenna Meneses de Almeida](https://github.com/lorennam)
- [Bento Guilherme Gomes Oliveira](https://github.com/bnnto)

## Principais Funcionalidades

**Busca e Descoberta**
- **Busca ao vivo:** Os resultados aparecem enquanto você digita (a cada pausa de 300 ms), sem precisar apertar Enter, com até 10 jogos por consulta.
- **Filtro por gênero e ordenação:** Refinamento dos resultados por gênero e ordenação por Relevância ou Nome (A-Z).
- **Capas em alta resolução:** A capa é trocada por uma versão HD apenas na exibição, enquanto o banco guarda a URL original. Jogos sem capa recebem uma imagem padrão.
- **Cache de consultas:** Buscas repetidas são reaproveitadas por 10 minutos, reduzindo chamadas à API.

**Gestão da Biblioteca**
- **Três status de acompanhamento:** Quero jogar, Jogando e Finalizado, cada um com sua própria aba.
- **Adicionar e alterar status:** Menu em cada card de resultado ("Adicionar" ou "Alterar status"). Clicar de novo no mesmo jogo nunca duplica o registro.
- **Horas jogadas:** Soma de horas direto no card (por exemplo, 2.5 + 1 = `3.5 h`), com valor preservado após recarregar a página.
- **Remoção com confirmação:** O jogo só é apagado depois de uma confirmação explícita, que avisa que as horas também serão perdidas.
- **Persistência local:** Tudo é salvo em SQLite e sobrevive ao F5 e ao reinício do servidor.

**Estatísticas**
- **KPIs:** Total de jogos no backlog, horas jogadas, jogos em andamento e jogos finalizados.
- **Distribuição por status:** Gráfico de rosca com a proporção de cada status.
- **Horas por status:** Gráfico de colunas com o tempo investido em cada grupo.
- **Jogos por gênero:** Barras horizontais com os gêneros mais frequentes da biblioteca.
- **Lista "Todos os jogos":** Visão consolidada com capa, gêneros, status e horas de cada título.

**Recursos Transversais**
- **Renovação automática de token:** O token da IGDB é reaproveitado enquanto válido e renovado com margem de segurança, com uma retentativa automática caso a consulta falhe.
- **Tratamento de erros na fronteira:** Falhas de rede ou de banco de dados viram mensagens claras na tela, sem quebrar o app.
- **Interface própria:** Tema escuro com CSS customizado, navegação lateral com ícones, cards em grade responsiva (5 → 3 → 2 colunas) e estados vazios orientativos.
- **Movimento e acessibilidade:** Animações curtas em `transform` e `opacity`, hover apenas em dispositivos com mouse, versão só-fade para `prefers-reduced-motion` e foco visível nos botões.

## Tech Stack

### Interface
| Tecnologia | Função |
|---|---|
| **Streamlit** | Framework para construção da interface web em Python |
| **streamlit-keyup** | Componente de busca ao vivo, sem necessidade de Enter |
| **HTML/CSS puro** | Estilo próprio (`ESTILO`) e gráficos desenhados sem JavaScript |
| **Material Icons** | Ícones da navegação e dos botões |

### Dados e Integrações
| Tecnologia | Função |
|---|---|
| **IGDB API** | Fonte dos dados dos jogos (nome, capa, gêneros) |
| **Twitch Developers** | Emissão do token de acesso usado pela IGDB (OAuth com `client_id` e `client_secret`) |
| **Requests** | Chamadas HTTP com `timeout` de 10 segundos |
| **SQLite** | Persistência local do backlog, em `dados/backlog.db` |

### Qualidade e Paradigma
| Tecnologia | Função |
|---|---|
| **Testes em Python** | Scripts executados como módulos (`python -m tests.<nome>`) para funções puras e armazenamento |
| **Paradigma funcional** | Somente `lambda`, `map`, `filter`, `reduce` e expressões condicionais |
| **Imutabilidade** | Funções como `somar_horas` devolvem um novo jogo em vez de alterar o existente |

## Como Rodar Localmente

**Pré-requisitos**
- Python 3
- Conta no [Twitch Developers](https://dev.twitch.tv/) com um aplicativo registrado (a IGDB usa a autenticação da Twitch)

**1. Clonar o repositório**
```bash
git clone <url-do-repositorio>
cd biblioteca-de-jogos
```

**2. Criar o ambiente virtual e instalar dependências**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configurar as credenciais**
Crie o arquivo `.streamlit/secrets.toml` com o `client_id` e o `client_secret` do seu aplicativo, no topo do arquivo, em minúsculas e entre aspas (sem seção):
```toml
client_id = "<seu-client-id>"
client_secret = "<seu-client-secret>"
```
Este arquivo está no `.gitignore` e nunca deve ser versionado.

**4. Iniciar o app**
```bash
python -m streamlit run app.py
```
A aplicação estará disponível em `http://localhost:8501`. Na primeira execução, o banco `dados/backlog.db` é criado vazio automaticamente.

**Executando os testes**
A partir da raiz do projeto:
```bash
python -m tests.teste                # limpar_texto_busca, montar_consulta, contagem_por_genero
python -m tests.teste_token          # vencimento, validade e renovação do token
python -m tests.teste_traducao       # tradução do jogo vindo da IGDB
python -m tests.teste_regras         # regras de status, somar_horas e estatísticas
python -m tests.teste_armazenamento  # ler, salvar, upsert, horas, remover e banco corrompido
```

## Estrutura do Projeto

```text
biblioteca-de-jogos/
├── app.py                      # Ponto de entrada do Streamlit (só interface)
│
├── src/
│   ├── igdb/
│   │   └── cliente.py          # I/O: token (com vencimento) e consulta à IGDB
│   ├── dominio/
│   │   ├── regras.py           # Puras: estados válidos, normalizar_status, somar_horas
│   │   ├── traducao.py         # Puras: limpar_texto_busca, traduzir_jogo, CAPA_PADRAO
│   │   └── estatisticas.py     # Puras: filtros, totais e contagens
│   ├── armazenamento/
│   │   └── backlog_sqlite.py   # I/O: ler, salvar, atualizar horas e remover no SQLite
│   └── interface/
│       └── estilo.py           # Folha de estilo do app (somente dados)
│
├── tests/                      # teste.py, teste_token.py, teste_traducao.py,
│                               # teste_regras.py, teste_armazenamento.py
├── dados/
│   └── backlog.db              # Dados do usuário (criado automaticamente)
├── .streamlit/
│   └── secrets.toml            # Credenciais da IGDB (fora do versionamento)
├── .gitignore
└── requirements.txt
```

## Arquitetura
O sistema adota uma arquitetura simples, com clara separação de responsabilidades:
- **Interface fina:** O `app.py` só desenha a tela e liga os botões às funções. Navegação por botões na barra lateral, com a página atual guardada em `st.session_state`.
- **Regras puras:** Toda a lógica (validação de status, soma de horas, tradução dos dados da IGDB, estatísticas) fica em `src/dominio/`, sem efeitos colaterais, o que garante determinismo e facilita os testes.
- **I/O isolado:** Rede (`cliente.py`) e banco de dados (`backlog_sqlite.py`) ficam em módulos próprios. Cada operação de banco abre e fecha a própria conexão, o que é seguro com as threads do Streamlit.
- **Validação antes da gravação:** O status é validado e normalizado em Python antes de abrir o banco, e o *upsert* preserva as horas quando o mesmo jogo troca de status.
- **Erros na fronteira:** Um único `try` no `app.py` captura falhas de rede (`requests.RequestException`) e de armazenamento (`ERROS_ARMAZENAMENTO`), enquanto as funções internas deixam o erro subir ou o convertem em `None`.
- **Efeitos encadeados sem `def`:** Operações com efeito colateral usam a "tupla com `[-1]`" (executa da esquerda para a direita e devolve o último item) e lambdas aninhadas para guardar valores intermediários.
- **Segurança por padrão:** Credenciais ficam em `.streamlit/secrets.toml`, fora do repositório, e todo texto exibido na interface é escapado antes de virar HTML.