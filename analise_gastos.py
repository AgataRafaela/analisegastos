"""
analise de gastos pessoais com categorização automática.

uso:
    python analise_gastos.py extrato_exemplo.csv
    python analise_gastos.py extrato.csv --usar-llm        # classifica o que sobrar com IA (opcional)
    python analise_gastos.py fatura.csv --gastos-positivos # bancos que exportam gasto como valor positivo
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# 1. CONFIGURAÇÃO

# palavras-chave (sem acento, minusculas) -> categoria. A ordem importa: a primeira regra que bater vence
REGRAS = {
    "Transporte": ["uber", "99 pop", "99pop", "posto", "ipiranga", "shell", "estacionamento", "sem parar"],
    "Alimentação": ["mercado", "ifood", "restaurante", "padaria", "lanchonete", "supermercado", "acougue"],
    "Moradia": ["aluguel", "condominio", "enel", "sabesp", "claro internet", "vivo fibra"],
    "Assinaturas": ["netflix", "spotify", "disney", "prime video", "youtube premium"],
    "Saúde": ["drogasil", "farmacia", "droga raia", "hospital", "unimed", "smart fit", "academia"],
    "Lazer": ["cinema", "cinemark", "livraria", "steam", "ingresso"],
    "Compras": ["amazon", "mercado livre", "shopee", "magalu"],
}

CATEGORIAS = list(REGRAS) + ["Outros"]

# nomes alternativos de colunas que cada banco usa
ALIASES_COLUNAS = {
    "data": ["data", "date", "data lancamento", "data da compra"],
    "descricao": ["descricao", "historico", "lancamento", "title", "estabelecimento", "description"],
    "valor": ["valor", "amount", "value", "valor (r$)"],
}

CACHE_PATH = Path("cache_categorias.json")

# 2. LEITURA E LIMPEZA

def remover_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def para_float(valor) -> float:
    """Converte '1.234,56', '-23,90' ou '-23.90' em float."""
    s = str(valor).replace("R$", "").strip()
    if "," in s:  # formato brasileiro: ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    return float(s)


def ler_extrato(caminho: str) -> pd.DataFrame:
    """lê CSV/Excel de qualquer banco e devolve colunas: data, descricao, valor."""
    caminho = Path(caminho)
    if caminho.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(caminho, dtype=str)
    else:
        try:
            df = pd.read_csv(caminho, sep=None, engine="python", dtype=str, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(caminho, sep=None, engine="python", dtype=str, encoding="latin-1")

    # normaliza nomes das colunas e mapeia para o padrao
    df.columns = [remover_acentos(c).strip().lower() for c in df.columns]
    renomear = {}
    for padrao, opcoes in ALIASES_COLUNAS.items():
        for col in df.columns:
            if col in opcoes:
                renomear[col] = padrao
                break
    df = df.rename(columns=renomear)

    faltando = {"data", "descricao", "valor"} - set(df.columns)
    if faltando:
        raise ValueError(
            f"Colunas não encontradas: {faltando}. Colunas do arquivo: {list(df.columns)}. "
            "Ajuste ALIASES_COLUNAS para o formato do seu banco."
        )

    df = df[["data", "descricao", "valor"]].dropna()
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = df["valor"].map(para_float)
    return df


def limpar_descricao(desc: str) -> str:
    """'COMPRA CARTAO 1234 Padaria Pão Quente' -> 'padaria pao quente'."""
    d = remover_acentos(desc).lower()
    d = re.sub(r"\b(compra cartao|compra no debito|pix enviado|pix recebido)\b", " ", d)
    d = re.sub(r"[*\-_/]", " ", d)
    d = re.sub(r"\b\d+\b", " ", d)  # remove números soltos (finais de cartão, códigos)
    return re.sub(r"\s+", " ", d).strip()


# 3. CATEGORIZAÇÃO

def categorizar_por_regras(desc_original: str) -> str:
    d = re.sub(r"[*\-_/]", " ", remover_acentos(desc_original).lower())
    d = re.sub(r"\s+", " ", d)
    for categoria, palavras in REGRAS.items():
        if any(p in d for p in palavras):
            return categoria
    return "Outros"


def carregar_cache() -> dict:
    return json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}


def categorizar_com_llm(descricoes: list[str], lote: int = 40) -> dict:
    """classifica descrições desconhecidas com a API do Claude (requer ANTHROPIC_API_KEY).

    privacidade: nomes de pessoas em PIX são enviados à API.
    considere anonimizar antes de usar com dados reais.
    """
    import anthropic  # importado aqui para o resto do script funcionar sem a lib

    cache = carregar_cache()
    pendentes = [d for d in descricoes if d not in cache]
    client = anthropic.Anthropic()

    for i in range(0, len(pendentes), lote):
        grupo = pendentes[i : i + lote]
        prompt = (
            f"Classifique cada descrição de extrato bancário brasileiro em UMA destas categorias: "
            f"{', '.join(CATEGORIAS)}.\n"
            "Responda APENAS com um objeto JSON {descricao: categoria}, sem texto extra.\n\n"
            + json.dumps(grupo, ensure_ascii=False)
        )
        resposta = client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = resposta.content[0].text.strip()
        texto = re.sub(r"^```(?:json)?|```$", "", texto, flags=re.MULTILINE).strip()
        try:
            resultado = json.loads(texto)
        except json.JSONDecodeError:
            continue  # lote mal formado: fica como "outros"
        for desc, cat in resultado.items():
            cache[desc] = cat if cat in CATEGORIAS else "Outros"

    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return cache

# 4. VISUALIZAÇÃO

def plotar(gastos: pd.DataFrame, mostrar: bool) -> None:
    por_categoria = gastos.groupby("categoria")["valor_abs"].sum().sort_values(ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.pie(por_categoria, labels=por_categoria.index, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Para onde está indo o seu dinheiro")

    por_mes = gastos.pivot_table(
        index=gastos["data"].dt.to_period("M").astype(str),
        columns="categoria",
        values="valor_abs",
        aggfunc="sum",
        fill_value=0,
    )
    por_mes.plot(kind="bar", stacked=True, ax=ax2, rot=0)
    ax2.set_title("Gastos por mês")
    ax2.set_xlabel("")
    ax2.set_ylabel("R$")

    plt.tight_layout()
    plt.savefig("grafico_gastos.png", dpi=150)
    print("Gráfico salvo em grafico_gastos.png")
    if mostrar:
        plt.show()

# 5. EXECUÇÃO

def main() -> None:
    ap = argparse.ArgumentParser(description="Análise de gastos com categorização automática")
    ap.add_argument("arquivo", help="extrato em CSV ou Excel")
    ap.add_argument("--usar-llm", action="store_true", help="classifica com IA o que as regras não pegarem")
    ap.add_argument("--gastos-positivos", action="store_true", help="o banco exporta gastos como valores positivos")
    ap.add_argument("--mostrar", action="store_true", help="abre o gráfico em uma janela")
    args = ap.parse_args()

    df = ler_extrato(args.arquivo)
    if args.gastos_positivos:
        df["valor"] = -df["valor"]

    df["categoria"] = df["descricao"].map(categorizar_por_regras)

    if args.usar_llm:
        sobras = df.loc[df["categoria"] == "Outros", "descricao"].map(limpar_descricao).unique().tolist()
        if sobras:
            mapa = categorizar_com_llm(sobras)
            mascara = df["categoria"] == "Outros"
            df.loc[mascara, "categoria"] = (
                df.loc[mascara, "descricao"].map(limpar_descricao).map(mapa).fillna("Outros")
            )

    # so saídas entram na análise (entradas, como salário, ficam de fora)
    gastos = df[df["valor"] < 0].copy()
    gastos["valor_abs"] = gastos["valor"].abs()

    resumo = gastos.groupby("categoria")["valor_abs"].sum().sort_values(ascending=False)
    print("\nTotal gasto por categoria (R$):")
    print(resumo.round(2).to_string())
    print(f"\nTotal geral: R$ {resumo.sum():.2f}")

    nao_classificados = gastos.loc[gastos["categoria"] == "Outros", "descricao"].unique()
    if len(nao_classificados):
        print("\nSem categoria (adicione regras ou use --usar-llm):")
        for d in nao_classificados:
            print(f"  - {d}")

    plotar(gastos, args.mostrar)


if __name__ == "__main__":
    main()