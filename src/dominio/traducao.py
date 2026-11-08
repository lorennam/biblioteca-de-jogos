# funções puras: traduzir_jogo, limpeza do texto

limpar_texto_busca = lambda texto: (
    texto.strip().replace('"', '')
    if texto and texto.strip().replace('"', '')
    else None
)

entrada_normal = "The Witcher"
entrada_com_aspas_e_espacos = '  "Zelda"  '
entrada_so_espacos = "     "

print("Normal:", repr(limpar_texto_busca(entrada_normal)))
print("Com aspas/espaços:", repr(limpar_texto_busca(entrada_com_aspas_e_espacos)))
print("Só espaços:", repr(limpar_texto_busca(entrada_so_espacos)))