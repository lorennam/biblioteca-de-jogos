from src.dominio.traducao import traduzir_jogo, CAPA_PADRAO

item_completo = {
    "id": 1022,
    "name": "The Legend of Zelda",
    "cover": {"url": "//images.igdb.com/igdb/image/upload/t_thumb/co1uii.jpg"},
    "genres": [{"name": "Adventure"}],
}
jogo = traduzir_jogo(item_completo)
assert jogo["id"] == 1022
assert jogo["nome"] == "The Legend of Zelda"
assert jogo["capa"] == "https://images.igdb.com/igdb/image/upload/t_thumb/co1uii.jpg"
assert jogo["genero"] == ["Adventure"]
assert "status" not in jogo

sem_capa_nem_genero = traduzir_jogo({"id": 2, "name": "Sem Dados"})
assert sem_capa_nem_genero["capa"] == CAPA_PADRAO
assert sem_capa_nem_genero["genero"] == []

muitos_generos = traduzir_jogo({
    "id": 3, "name": "Variado",
    "genres": [{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}],
})
assert muitos_generos["genero"] == ["A", "B", "C"]

print("traduzir_jogo: ok")