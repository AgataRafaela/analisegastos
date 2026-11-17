from gastos.anonimizacao import anonimizar, preparar_para_envio


def test_remove_cpf():
    resultado = anonimizar("TRANSF 123.456.789-00 MARIA")
    assert "123.456.789-00" not in resultado


def test_remove_email():
    resultado = anonimizar("PAGAMENTO joao@email.com")
    assert "joao@email.com" not in resultado


def test_pix_esconde_o_nome():
    resultado = anonimizar("PIX ENVIADO MARIA SOUZA")
    assert "MARIA" not in resultado
    assert "SOUZA" not in resultado
    assert "[pessoa]" in resultado


def test_descricao_de_loja_continua_igual():
    assert anonimizar("NETFLIX.COM") == "NETFLIX.COM"


def test_preparar_para_envio_limpa_e_anonimiza():
    resultado = preparar_para_envio("PIX ENVIADO JOAO PEREIRA")
    assert resultado == "pix enviado [pessoa]"
