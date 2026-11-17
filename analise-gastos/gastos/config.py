"""Configurações do projeto: categorias, regras e nomes de colunas."""

from pathlib import Path

# Palavras-chave (sem acento, minúsculas) -> categoria.
# A ordem importa: a primeira categoria que bater vence.
REGRAS = {
    "Transporte": ["uber", "99 pop", "99pop", "posto", "ipiranga", "shell", "estacionamento", "sem parar"],
    "Alimentação": ["mercado", "ifood", "restaurante", "padaria", "lanchonete", "supermercado", "acougue"],
    "Moradia": ["aluguel", "condominio", "enel", "sabesp", "claro internet", "vivo fibra"],
    "Assinaturas": ["netflix", "spotify", "disney", "prime video", "youtube premium"],
    "Saúde": ["drogasil", "farmacia", "droga raia", "hospital", "unimed", "smart fit", "academia"],
    "Lazer": ["cinema", "cinemark", "livraria", "steam", "ingresso"],
    "Compras": ["amazon", "mercado livre", "shopee", "magalu"],
    # fica por último para que "PIX ENVIADO MERCADO SILVA" caia em Alimentação
    "Transferências": ["pix enviado", "transferencia"],
}

CATEGORIAS = list(REGRAS) + ["Outros"]

# Nomes que cada banco usa para as colunas (já sem acento e em minúsculas)
ALIASES_COLUNAS = {
    "data": ["data", "date", "data lancamento", "data da compra"],
    "descricao": ["descricao", "historico", "lancamento", "title", "estabelecimento", "description"],
    "valor": ["valor", "amount", "value", "valor (r$)"],
}

CACHE_PATH = Path("cache_categorias.json")
MODELO_LLM = "claude-haiku-5-5"
