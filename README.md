# análise de gastos pessoais com python

lê o extrato bancário (CSV ou Excel), categoriza cada gasto e gera gráficos.
A categorização usa regras por palavra-chave e opcionalmente, a API do Claude para as transações que as regras não reconhecem.

## instalação

```bash
pip install -r requirements.txt
```

## uso

```bash
python main.py extrato_exemplo.csv                # só regras
python main.py extrato_exemplo.csv --ver-envio    # mostra o que iria para a IA
python main.py extrato_exemplo.csv --usar-llm     # regras + IA (precisa de API key)
```

para usar a IA, defina a variável de ambiente `ANTHROPIC_API_KEY`.

## estrutura

```
main.py                  # linha de comando
gastos/
  config.py              # categorias, regras e nomes de colunas
  leitura.py             # lê CSV/Excel e padroniza as colunas
  utils.py               # funções de limpeza de texto
  categorias.py          # categorização por regras e aplicação do resultado da IA
  anonimizacao.py        # remove dados pessoais antes de enviar para a IA
  llm.py                 # conversa com a API do Claude
  graficos.py            # gráfico de pizza e barras por mês
tests/                   # testes com pytest
```

## testes

```bash
pytest
```

## privacidade

nenhum valor, data ou entrada (salário) é enviado para a IA. Só descrições de
gastos não reconhecidos pelas regras, depois de anonimizadas. Use `--ver-envio`
para conferir antes. NÃO coloque extratos reais no Git (veja o `.gitignore`).
