def avaliar_condicao(cond, dados):
    valor = dados.get(cond["campo"])

    if valor is None:
        return False

    if cond["op"] == "<":
        return valor < cond["valor"]
    elif cond["op"] == ">":
        return valor > cond["valor"]
    elif cond["op"] == "==":
        return valor == cond["valor"]
    elif cond["op"] == "<=":
        return valor <= cond["valor"]  # CORREÇÃO: era <=["valor"]

    return False


def aplicar_regras(dados, regras):
    resultados = []

    for regra in regras:
        if all(avaliar_condicao(c, dados) for c in regra["condicoes"]):
            resultados.append(regra["acao"])

    return resultados


# Sinais monitorados para detectar piora simultânea (E2)
# Cada entrada é (campo, "piora quando") — True = piora quando sobe, False = piora quando cai
_SINAIS_MONITORADOS = [
    ("spo2",               False),  # piora quando CAI
    ("temperatura",        True),   # piora quando SOBE
    ("frequencia_cardiaca",True),   # piora quando SOBE (fora da faixa normal)
    ("escala_dor",         True),   # piora quando SOBE
    ("glasgow",            False),  # piora quando CAI
    ("vomitos_por_hora",   True),   # piora quando SOBE
]

def detectar_piora(leitura_ant, leitura_atual):
    """
    Retorna o número de sinais vitais que pioraram entre duas leituras.
    E2 exige que DOIS OU MAIS sinais piorem simultaneamente.
    """
    pioras = 0

    for campo, piora_quando_sobe in _SINAIS_MONITORADOS:
        ant = leitura_ant.get(campo)
        atu = leitura_atual.get(campo)

        if ant is None or atu is None:
            continue  # campo ausente não conta como piora

        if piora_quando_sobe and atu > ant:
            pioras += 1
        elif not piora_quando_sobe and atu < ant:
            pioras += 1

    return pioras


def aplicar_regras_segunda_ordem(estado, leitura_anterior, leitura_atual):
    """
    Avalia as regras de segunda ordem E1–E5.
    Retorna lista de mensagens com cada regra disparada (pode ser mais de uma).
    """
    eventos = []

    # --- E2: dois ou mais sinais vitais pioraram simultaneamente ---
    # SE dois ou mais sinais vitais pioraram simultaneamente na última leitura,
    # ENTÃO elevar prioridade em 1 grau e agendar nova leitura em 5 minutos.
    qtd_pioras = detectar_piora(leitura_anterior, leitura_atual)
    if qtd_pioras >= 2:
        estado["nivel"] = max(1, estado["nivel"] - 1)  # eleva (nível menor = mais urgente)
        estado["proxima_leitura_minutos"] = 5           # agenda reavaliação
        eventos.append(
            f"E2 aplicada: {qtd_pioras} sinais vitais pioraram simultaneamente — "
            f"nível elevado para {estado['nivel']}, nova leitura em 5 min"
        )

    return eventos if eventos else [None]