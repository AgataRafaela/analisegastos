from gastos.utils import limpar_descricao, normalizar


def test_normalizar():
    assert normalizar("  Padaria   PÃO Quente ") == "padaria pao quente"


def test_normalizar_tira_asterisco():
    assert normalizar("Uber *Trip") == "uber trip"


def test_limpar_descricao_tira_prefixo_e_numeros():
    assert limpar_descricao("COMPRA CARTAO 1234 Padaria Pão Quente") == "padaria pao quente"
