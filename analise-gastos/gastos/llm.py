"""Categorização com a API do Claude. Só recebe descrições já anonimizadas."""

import json
import os
import re

from gastos.config import CACHE_PATH, CATEGORIAS, MODELO_LLM


def carregar_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def salvar_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def montar_prompt(descricoes):
    return (
        "Classifique cada descrição de extrato bancário brasileiro em UMA destas categorias: "
        + ", ".join(CATEGORIAS)
        + ".\nResponda APENAS com um objeto JSON no formato {descricao: categoria}, sem texto extra.\n\n"
        + json.dumps(descricoes, ensure_ascii=False)
    )


def interpretar_resposta(texto):
    """Transforma a resposta da IA em dicionário. Se algo vier errado, devolve {}."""
    texto = re.sub(r"```(?:json)?", "", texto).strip()
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        return {}
    if not isinstance(dados, dict):
        return {}

    resultado = {}
    for descricao, categoria in dados.items():
        # se a IA inventar uma categoria que não existe, vira "Outros"
        resultado[descricao] = categoria if categoria in CATEGORIAS else "Outros"
    return resultado


def categorizar_com_llm(descricoes, tamanho_lote=40):
    """Manda as descrições (em lotes) para o Claude e devolve {descricao: categoria}."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("Variável de ambiente ANTHROPIC_API_KEY não encontrada.")

    import anthropic

    cache = carregar_cache()
    pendentes = [d for d in descricoes if d not in cache]
    client = anthropic.Anthropic()  # lê a chave da variável de ambiente

    for i in range(0, len(pendentes), tamanho_lote):
        lote = pendentes[i : i + tamanho_lote]
        resposta = client.messages.create(
            model=MODELO_LLM,
            max_tokens=1500,
            messages=[{"role": "user", "content": montar_prompt(lote)}],
        )
        cache.update(interpretar_resposta(resposta.content[0].text))

    salvar_cache(cache)
    return cache
