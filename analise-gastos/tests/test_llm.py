from gastos.llm import interpretar_resposta


def test_resposta_json_simples():
    resposta = '{"oficina do ze": "Transporte"}'
    assert interpretar_resposta(resposta) == {"oficina do ze": "Transporte"}


def test_resposta_com_bloco_de_codigo():
    resposta = '```json\n{"oficina do ze": "Transporte"}\n```'
    assert interpretar_resposta(resposta) == {"oficina do ze": "Transporte"}


def test_categoria_inventada_vira_outros():
    resposta = '{"oficina do ze": "Carros"}'
    assert interpretar_resposta(resposta) == {"oficina do ze": "Outros"}


def test_resposta_invalida_devolve_dicionario_vazio():
    assert interpretar_resposta("não consegui classificar") == {}
