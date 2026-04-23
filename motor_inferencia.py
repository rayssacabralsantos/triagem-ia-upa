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
        return valor <=["valor"]
    
    return False

def aplicar_regras(dados, regras):
    resultados = []

    print("DADOS:", dados)
    
    for regra in regras:
        print("Testando regra:", regra["nome"])
        if all(avaliar_condicao(c, dados) for c in regra["condicoes"]):
            resultados.append(regra["acao"])

    return resultados

def detectar_piora(leitura_ant, leitura_atual):
    pioras = 0

    if leitura_atual.get("spo2", 100) < leitura_ant.get("spo2", 100):
        pioras += 1
    if leitura_atual.get("temperatura", 0) > leitura_ant.get("temperatura", 0):
        pioras += 1

    return pioras >= 2

def aplicar_regras_segunda_ordem(estado, leitura_anterior, leitura_atual):
    pioras = 0

    if leitura_atual.get("spo2", 100) < leitura_anterior.get("spo2", 100):
        pioras += 1

    if leitura_atual.get("temperatura", 0) > leitura_anterior.get("temperatura", 0):
        pioras += 1

    if pioras >= 2:
        estado["nivel"] = max(1, estado["nivel"] - 1)
        return "E2 aplicada: piora em múltiplos sinais vitais"

    return None