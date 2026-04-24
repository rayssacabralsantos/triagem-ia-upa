# Ponto de entrada do sistema de triagem
#
# BUGS CORRIGIDOS:
#   - print(mensagem_e2) imprimia uma lista Python crua em vez de texto legível
#   - registrar() era chamado mesmo quando mensagem_e2 == [None]
#   - estado e log eram variáveis globais soltas; agora o fluxo usa processar()
#     do motor_inferencia, que encapsula tudo internamente
#   - ajustar_vulnerabilidade estava duplicado aqui e no motor; removido daqui

from motor_inferencia import processar
from pacientes import paciente_exemplo
from log import registrar, mostrar_log


def exibir_resultado(paciente):
    print(f"\n{'='*50}")
    print(f"Paciente: {paciente['id']} | Idade: {paciente['idade']}")
    print(f"{'='*50}")

    resultado = processar(paciente)

    print(f"\n✅ Nível final: {resultado['nivel_atual']}")

    if resultado["historico_niveis"]:
        print("\n📈 Histórico de classificações:")
        for hora, nivel in resultado["historico_niveis"]:
            print(f"   {hora} → Nível {nivel}")

    if resultado["eventos"]:
        print("\n⚡ Eventos de segunda ordem:")
        for evento in resultado["eventos"]:
            print(f"   • {evento}")

    if resultado["alertas"]:
        print("\n🚨 Alertas operacionais:")
        for alerta in resultado["alertas"]:
            print(f"   ⚠️  {alerta}")

    # Registra no log auditável
    for hora, nivel in resultado["historico_niveis"]:
        registrar(hora, "Classificação", {}, f"Nível {nivel}")
    for evento in resultado["eventos"]:
        hora_evento = paciente["leituras"][-1]["hora"]
        registrar(hora_evento, "Segunda ordem", {}, evento)

    return resultado


if __name__ == "__main__":
    exibir_resultado(paciente_exemplo)

    print("\n📋 LOG FINAL:")
    mostrar_log()