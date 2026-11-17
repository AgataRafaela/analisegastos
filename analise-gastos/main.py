"""
Análise de gastos pessoais com categorização automática.

Exemplos:
    python main.py extrato_exemplo.csv
    python main.py extrato_exemplo.csv --ver-envio     # mostra o que iria para a IA, sem enviar
    python main.py extrato_exemplo.csv --usar-llm      # categoriza o que sobrar com a IA
"""

import argparse

from gastos.categorias import aplicar_categorias_da_ia, categorizar_por_regras, descricoes_para_ia
from gastos.graficos import plotar
from gastos.leitura import ler_extrato
from gastos.llm import categorizar_com_llm


def main():
    parser = argparse.ArgumentParser(description="Análise de gastos com categorização automática")
    parser.add_argument("arquivo", help="extrato em CSV ou Excel")
    parser.add_argument("--usar-llm", action="store_true", help="categoriza com IA o que as regras não pegarem")
    parser.add_argument("--ver-envio", action="store_true", help="só mostra o que seria enviado para a IA")
    parser.add_argument("--gastos-positivos", action="store_true", help="o banco exporta gastos como valores positivos")
    parser.add_argument("--mostrar", action="store_true", help="abre o gráfico em uma janela")
    args = parser.parse_args()

    df = ler_extrato(args.arquivo)
    if args.gastos_positivos:
        df["valor"] = -df["valor"]

    df["categoria"] = df["descricao"].apply(categorizar_por_regras)

    if args.usar_llm or args.ver_envio:
        descricoes = descricoes_para_ia(df)

        if args.ver_envio:
            print("Isto é tudo que seria enviado para a IA (nenhum valor, nenhuma data):")
            for d in descricoes:
                print(f"  - {d}")
            return

        if descricoes:
            try:
                mapa = categorizar_com_llm(descricoes)
            except RuntimeError as erro:
                print(f"Erro: {erro}")
                return
            df = aplicar_categorias_da_ia(df, mapa)

    # só as saídas entram na análise (salário e outras entradas ficam de fora)
    gastos = df[df["valor"] < 0].copy()
    gastos["valor_abs"] = gastos["valor"].abs()

    resumo = gastos.groupby("categoria")["valor_abs"].sum().sort_values(ascending=False)
    print("\nTotal gasto por categoria (R$):")
    print(resumo.round(2).to_string())
    print(f"\nTotal geral: R$ {resumo.sum():.2f}")

    sem_categoria = gastos[gastos["categoria"] == "Outros"]["descricao"].unique()
    if len(sem_categoria) > 0:
        print("\nSem categoria (adicione regras em config.py ou use --usar-llm):")
        for d in sem_categoria:
            print(f"  - {d}")

    plotar(gastos, mostrar=args.mostrar)


if __name__ == "__main__":
    main()
