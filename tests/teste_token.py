from unittest.mock import MagicMock, patch

import src.igdb.cliente as cliente
from src.igdb.cliente import (
    calcular_expiracao,
    token_valido,
    montar_registro_token,
    consultar_com_renovacao,
)

# --- calcular_expiracao ---
assert calcular_expiracao(1000, 3600) == 4540          # 1000 + 3600 - 60
assert calcular_expiracao(1000, 3600, margem=0) == 4600

# --- token_valido ---
assert token_valido("abc", 2000, 1999) is True         # ainda no prazo
assert token_valido("abc", 2000, 2000) is False        # chegou no limite
assert token_valido("abc", 2000, 3000) is False        # vencido
assert token_valido(None, 2000, 1000) is False         # sem token
assert token_valido("", 2000, 1000) is False           # token vazio
assert token_valido("abc", 0.0, 1000) is False         # estado inicial da sessão

# --- montar_registro_token ---
assert montar_registro_token({"access_token": "abc", "expires_in": 3600}, 1000) == {
    "token": "abc",
    "expira_em": 4540,
}
sem_validade = montar_registro_token({"access_token": "abc"}, 1000)
assert token_valido(sem_validade["token"], sem_validade["expira_em"], 1000) is False

# --- obter_token (requests simulado, sem internet) ---
resposta_ok = MagicMock(status_code=200)
resposta_ok.json.return_value = {"access_token": "abc", "expires_in": 3600}
resposta_erro = MagicMock(status_code=400)

with patch.object(cliente.requests, "post", return_value=resposta_ok), \
     patch.object(cliente.time, "time", return_value=1000.0):
    assert cliente.obter_token("id", "segredo") == {"token": "abc", "expira_em": 4540.0}

with patch.object(cliente.requests, "post", return_value=resposta_erro):
    assert cliente.obter_token("id", "segredo") is None

# --- consultar_com_renovacao ---
# 1) token bom, consulta devolve lista vazia: nada de renovar
consultas, renovacoes = [], []
consultar = lambda t: (consultas.append(t), [])[-1]
renovar = lambda: (renovacoes.append(1), "novo")[-1]
assert consultar_com_renovacao(consultar, renovar, "velho") == []
assert consultas == ["velho"] and renovacoes == []

# 2) token velho falha (None), com o novo funciona: renova 1 vez e tenta de novo
consultas, renovacoes = [], []
consultar = lambda t: (consultas.append(t), ["jogo"] if t == "novo" else None)[-1]
assert consultar_com_renovacao(consultar, renovar, "velho") == ["jogo"]
assert consultas == ["velho", "novo"] and renovacoes == [1]

# 3) falha sempre: renova uma única vez e desiste (None)
consultas, renovacoes = [], []
consultar = lambda t: (consultas.append(t), None)[-1]
assert consultar_com_renovacao(consultar, renovar, "velho") is None
assert consultas == ["velho", "novo"] and renovacoes == [1]

# 4) sem token: não tenta renovar de novo
consultas, renovacoes = [], []
assert consultar_com_renovacao(consultar, renovar, None) is None
assert renovacoes == []

print("todos os testes de token passaram")