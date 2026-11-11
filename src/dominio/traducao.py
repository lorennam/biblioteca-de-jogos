limpar_texto_busca = lambda texto: (
    texto.strip().replace('"', '')
    if texto and texto.strip().replace('"', '')
    else None
)

CAPA_PADRAO = "https://placehold.co/90x128?text=Sem+capa"

traduzir_jogo = lambda item: {
    "id": item["id"],
    "nome": item["name"],
    "capa": ("https:" + item["cover"]["url"]) if "cover" in item else CAPA_PADRAO,
    "genero": list(map(lambda g: g["name"], item.get("genres", [])))[:3],
}