"""Leitura do extrato (CSV ou Excel) e padronização das colunas."""

from pathlib import Path

import pandas as pd

from gastos.config import ALIASES_COLUNAS
from gastos.utils import remover_acentos


def para_float(valor):
    """Converte '1.234,56', '-23,90' ou '-23.90' em número."""
    texto = str(valor).replace("R$", "").strip()
    if "," in texto:
        # formato brasileiro: ponto é milhar e vírgula é decimal
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


def ler_arquivo(caminho):
    caminho = Path(caminho)
    if caminho.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(caminho, dtype=str)
    try:
        return pd.read_csv(caminho, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(caminho, sep=None, engine="python", dtype=str, encoding="latin-1")


def ler_extrato(caminho):
    """Devolve um DataFrame com as colunas: data, descricao, valor."""
    df = ler_arquivo(caminho)

    # deixa os nomes das colunas em minúsculas e sem acento
    df.columns = [remover_acentos(c).strip().lower() for c in df.columns]

    # troca o nome que o banco usa pelo nome padrão
    renomear = {}
    for nome_padrao, opcoes in ALIASES_COLUNAS.items():
        for coluna in df.columns:
            if coluna in opcoes:
                renomear[coluna] = nome_padrao
                break
    df = df.rename(columns=renomear)

    faltando = {"data", "descricao", "valor"} - set(df.columns)
    if faltando:
        raise ValueError(
            f"Colunas não encontradas: {faltando}. "
            f"Colunas do arquivo: {list(df.columns)}. "
            "Ajuste ALIASES_COLUNAS em config.py."
        )

    df = df[["data", "descricao", "valor"]].dropna()
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = df["valor"].map(para_float)
    return df
