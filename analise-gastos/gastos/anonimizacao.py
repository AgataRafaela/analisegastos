"""Remove dados pessoais das descrições antes de mandar qualquer coisa para a API."""

import re

from gastos.utils import limpar_descricao

# (padrão, o que vai no lugar). A ordem importa: CNPJ antes de CPF.
PADROES = [
    (r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", "[cnpj]"),
    (r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[cpf]"),
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]"),
    (r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}", "[telefone]"),
    (r"\d{5,}", "[numero]"),  # qualquer sequência longa de dígitos (conta, agência etc.)
]


def anonimizar(descricao):
    texto = descricao
    for padrao, troca in PADROES:
        texto = re.sub(padrao, troca, texto)

    # Em PIX/TED, tudo que vem depois da palavra é nome de pessoa
    texto = re.sub(
        r"\b(pix enviado|pix recebido|pix|ted|transfer[eê]ncia)\b.*",
        r"\1 [pessoa]",
        texto,
        flags=re.IGNORECASE,
    )
    return texto


def preparar_para_envio(descricao):
    """Anonimiza e limpa a descrição. É isso (e só isso) que vai para a IA."""
    return limpar_descricao(anonimizar(descricao))
