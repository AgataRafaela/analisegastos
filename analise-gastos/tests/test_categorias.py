import pandas as pd

from gastos.categorias import aplicar_categorias_da_ia, categorizar_por_regras, descricoes_para_ia


def test_uber_e_transporte():
    assert categorizar_por_regras("Uber *Trip") == "Transporte"


def test_mercado_e_alimentacao():
    assert categorizar_por_regras("Mercado Silva") == "Alimentação"


def test_maiusculas_e_acentos_nao_atrapalham():
    assert categorizar_por_regras("FARMÁCIA POPULAR") == "Saúde"


def test_simbolo_no_meio_da_descricao():
    # "99 *POP" tem um asterisco que antes impedia de bater com "99 pop"
    assert categorizar_por_regras("99 *POP") == "Transporte"


def test_descricao_desconhecida_vira_outros():
    assert categorizar_por_regras("OFICINA DO ZE AUTO CENTER") == "Outros"


def test_pix_para_mercado_e_alimentacao():
    # a regra de alimentação vem antes da de transferências
    assert categorizar_por_regras("PIX ENVIADO MERCADO SILVA") == "Alimentação"


def test_descricoes_para_ia_so_pega_outros_e_sem_repetir():
    df = pd.DataFrame(
        {
            "descricao": ["Uber *Trip", "OFICINA DO ZE", "OFICINA DO ZE"],
            "valor": [-20.0, -350.0, -100.0],
            "categoria": ["Transporte", "Outros", "Outros"],
        }
    )
    assert descricoes_para_ia(df) == ["oficina do ze"]


def test_descricoes_para_ia_ignora_entradas():
    df = pd.DataFrame(
        {
            "descricao": ["SALARIO EMPRESA XYZ LTDA"],
            "valor": [4500.0],
            "categoria": ["Outros"],
        }
    )
    assert descricoes_para_ia(df) == []


def test_aplicar_categorias_da_ia():
    df = pd.DataFrame(
        {
            "descricao": ["Uber *Trip", "OFICINA DO ZE"],
            "categoria": ["Transporte", "Outros"],
        }
    )
    mapa = {"oficina do ze": "Transporte"}

    resultado = aplicar_categorias_da_ia(df, mapa)

    assert list(resultado["categoria"]) == ["Transporte", "Transporte"]
