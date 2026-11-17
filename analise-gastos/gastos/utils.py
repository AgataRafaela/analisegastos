"""Funções de texto usadas em várias partes do projeto."""

import re
import unicodedata


def remover_acentos(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acento e sem símbolos como * - _ /"""
    texto = remover_acentos(texto).lower()
    texto = re.sub(r"[*\-_/]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def limpar_descricao(descricao):
    """'COMPRA CARTAO 1234 Padaria Pão Quente' -> 'padaria pao quente'"""
    texto = normalizar(descricao)
    texto = re.sub(r"\b(compra cartao|compra no debito)\b", " ", texto)
    texto = re.sub(r"\b\d+\b", " ", texto)  # números soltos (final do cartão, códigos)
    return re.sub(r"\s+", " ", texto).strip()
