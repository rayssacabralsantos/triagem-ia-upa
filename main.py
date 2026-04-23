from base_conhecimento import regras
from motor_inferencia import aplicar_regras, aplicar_regras_segunda_ordem
from pacientes import paciente_exemplo
from log import registrar, mostrar_log


def ajustar_vulnerabilidade(nivel, paciente):
    if paciente["idade"] >= 60 or paciente["gestante"] or paciente["deficiencia"]:
        return max(1, nivel - 1)
    return nivel


# Estado do paciente
estado = {
    "nivel": None
}

leituras = paciente_exemplo["leituras"]

# Loop com índice 
for i in range(len(leituras)):
    leitura = leituras[i]

    print(f"\n📥 Processando leitura das {leitura['hora']}")

    # regras básicas
    resultados = aplicar_regras(leitura, regras)

    if resultados:
        niveis = [r["nivel"] for r in resultados]
        novo_nivel = min(niveis)

        # Não permite rebaixar prioridade
        if estado["nivel"] is None or novo_nivel < estado["nivel"]:
            estado["nivel"] = novo_nivel

        # Aplicar regra de vulnerabilidade
        estado["nivel"] = ajustar_vulnerabilidade(estado["nivel"], paciente_exemplo)

        mensagem = f"Paciente classificado como nível {estado['nivel']}"

        print(mensagem)

        registrar(
            leitura["hora"],
            "Classificação",
            leitura,
            mensagem
        )

    # Aplicar regras de segunda ordem
    if i > 0:
        mensagem_e2 = aplicar_regras_segunda_ordem(
            estado,
            leituras[i - 1],
            leitura
        )

        if mensagem_e2:
            print(mensagem_e2)

            registrar(
                leitura["hora"],
                "Regra E2",
                leitura,
                mensagem_e2
            )


# Mostrar log final
print("\n📋 LOG FINAL:")
mostrar_log()
