"""Gráficos: pizza por categoria e barras empilhadas por mês."""

import matplotlib.pyplot as plt


def plotar(gastos, mostrar=False, arquivo="grafico_gastos.png"):
    por_categoria = gastos.groupby("categoria")["valor_abs"].sum().sort_values(ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.pie(por_categoria, labels=por_categoria.index, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Para onde está indo o seu dinheiro")

    meses = gastos["data"].dt.to_period("M").astype(str)
    por_mes = gastos.pivot_table(
        index=meses, columns="categoria", values="valor_abs", aggfunc="sum", fill_value=0
    )
    por_mes.plot(kind="bar", stacked=True, ax=ax2, rot=0)
    ax2.set_title("Gastos por mês")
    ax2.set_xlabel("")
    ax2.set_ylabel("R$")

    plt.tight_layout()
    plt.savefig(arquivo, dpi=150)
    print(f"Gráfico salvo em {arquivo}")
    if mostrar:
        plt.show()
