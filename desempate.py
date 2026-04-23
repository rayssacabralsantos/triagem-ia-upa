def calcular_score(paciente):
    tempo = paciente.get("tempo_espera", 0)
    nivel = paciente.get("nivel", 5)
    piora = paciente.get("piora", 0)

    gravidade = 5 - nivel

    return tempo * 2 + gravidade * 5 + piora * 10

def ordenar_pacientes(lista):
    return sorted(lista, key=calcular_score, reverse=True)
