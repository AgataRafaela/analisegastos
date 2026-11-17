import pytest

from gastos.leitura import ler_extrato, para_float


def test_para_float_formato_brasileiro():
    assert para_float("-23,90") == -23.90
    assert para_float("1.234,56") == 1234.56


def test_para_float_formato_com_ponto():
    assert para_float("-23.90") == -23.90


def test_ler_extrato_csv(tmp_path):
    arquivo = tmp_path / "extrato.csv"
    arquivo.write_text(
        "Data;Descrição;Valor\n"
        "03/09/2026;Uber *Trip;-23,90\n"
        "05/09/2026;SALARIO;4500,00\n",
        encoding="utf-8",
    )

    df = ler_extrato(arquivo)

    assert list(df.columns) == ["data", "descricao", "valor"]
    assert len(df) == 2
    assert df["valor"].iloc[0] == -23.90
    assert df["data"].iloc[0].month == 9


def test_ler_extrato_sem_coluna_de_valor(tmp_path):
    arquivo = tmp_path / "extrato.csv"
    arquivo.write_text("Data;Descrição\n03/09/2026;Uber\n", encoding="utf-8")

    with pytest.raises(ValueError):
        ler_extrato(arquivo)
