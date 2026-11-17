"""Categorização das transações: primeiro por regras, depois (opcional) pela IA."""

from gastos.anonimizacao import preparar_para_envio
from gastos.config import REGRAS
from gastos.utils import normalizar


def categorizar_por_regras(descricao):
    texto = normalizar(descricao)
    for categoria, palavras in REGRAS.items():
        for palavra in palavras:
            if palavra in texto:
                return categoria
    return "Outros"


def descricoes_para_ia(df):
    """Descrições anonimizadas e sem repetição dos GASTOS que ficaram em 'Outros'.

    Entradas (salário, por exemplo) nunca vão para a IA, porque não entram no gráfico
    e costumam ter o nome do empregador.
    """
    sobras = df[(df["categoria"] == "Outros") & (df["valor"] < 0)]["descricao"]
    return sorted(set(preparar_para_envio(d) for d in sobras))


def aplicar_categorias_da_ia(df, mapa):
    """Troca 'Outros' pela categoria que a IA devolveu (mapa: descrição anonimizada -> categoria)."""
    df = df.copy()
    for indice, linha in df.iterrows():
        if linha["categoria"] == "Outros":
            chave = preparar_para_envio(linha["descricao"])
            df.loc[indice, "categoria"] = mapa.get(chave, "Outros")
    return df
