from base_conhecimento import regras, SLA_POR_NIVEL

# ---------------------------------------------------------------------------
# Avaliador de condições individuais
# CORRIGIDO: operador ">=" estava ausente — regras de dor moderada (5-7)
# e FC (120-150) nunca disparavam.
# ---------------------------------------------------------------------------

def avaliar_condicao(cond, dados):
    valor = dados.get(cond["campo"])

    if valor is None:
        return False

    op    = cond["op"]
    alvo  = cond["valor"]

    if op == "<":   return valor < alvo
    if op == ">":   return valor > alvo
    if op == "==":  return valor == alvo
    if op == "<=":  return valor <= alvo
    if op == ">=":  return valor >= alvo   # CORRIGIDO: estava ausente

    return False


# ---------------------------------------------------------------------------
# Aplicador de regras primárias
# Retorna o nível mais urgente (menor número) ou None se nenhuma regra disparou.
# ---------------------------------------------------------------------------

def aplicar_regras(dados):
    nivel_mais_urgente = None

    for regra in regras:
        if all(avaliar_condicao(c, dados) for c in regra["condicoes"]):
            nivel = regra["acao"]["nivel"]
            if nivel_mais_urgente is None or nivel < nivel_mais_urgente:
                nivel_mais_urgente = nivel

    return nivel_mais_urgente


# ---------------------------------------------------------------------------
# Detecção de piora simultânea entre leituras
# ---------------------------------------------------------------------------

_SINAIS_MONITORADOS = [
    ("spo2",                False),  # piora quando CAI
    ("temperatura",         True),   # piora quando SOBE
    ("frequencia_cardiaca", True),   # piora quando SOBE
    ("escala_dor",          True),   # piora quando SOBE
    ("glasgow",             False),  # piora quando CAI
    ("vomitos_por_hora",    True),   # piora quando SOBE
]

def detectar_piora(leitura_ant, leitura_atual):
    """Retorna número de sinais vitais que pioraram entre duas leituras."""
    pioras = 0

    for campo, piora_quando_sobe in _SINAIS_MONITORADOS:
        ant = leitura_ant.get(campo)
        atu = leitura_atual.get(campo)

        if ant is None or atu is None:
            continue   # campo ausente não conta como piora

        if piora_quando_sobe and atu > ant:
            pioras += 1
        elif not piora_quando_sobe and atu < ant:
            pioras += 1

    return pioras


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_hora(hora_str):
    """Converte 'HH:MM' para minutos totais desde meia-noite."""
    h, m = hora_str.split(":")
    return int(h) * 60 + int(m)


def _ajustar_vulnerabilidade(nivel, paciente):
    """Eleva 1 grau para grupos vulneráveis (Resolução SUS 2017)."""
    if (paciente.get("idade", 0) >= 60
            or paciente.get("gestante", False)
            or paciente.get("deficiencia", False)):
        return max(1, nivel - 1)
    return nivel


# ---------------------------------------------------------------------------
# Regras de segunda ordem (E1–E5)
#
# ORDEM DE AVALIAÇÃO IMPORTA:
#   E1 → E2 → E3 → E5 → E4
#
# E4 é avaliada por último porque força exatamente Nível 2, e só deve
# sobrescrever quando o nível ainda não for mais urgente que 2.
# Se o paciente já estiver em Nível 1 (por E2 ou classificação primária),
# E4 não rebaixa — respeita a restrição de não rebaixamento.
# ---------------------------------------------------------------------------

def aplicar_regras_segunda_ordem(estado, leitura_anterior, leitura_atual, paciente):
    """
    Avalia E1–E5 e modifica estado in-place.
    Retorna lista de strings com cada evento gerado.
    """
    eventos = []
    nivel_antes_segunda_ordem = estado["nivel"]

    # --- E1: reclassificação de Nível 3 → 2 em < 30 min ---
    nivel_anterior = estado.get("nivel_anterior")
    if nivel_anterior == 3 and estado["nivel"] == 2:
        minutos = _parse_hora(leitura_atual["hora"]) - _parse_hora(leitura_anterior["hora"])
        if minutos < 30:
            eventos.append(
                f"E1: reclassificação crítica de Nível 3 → 2 em {minutos} min "
                f"— médico de plantão notificado"
            )

    # --- E2: dois ou mais sinais pioraram simultaneamente ---
    qtd_pioras = detectar_piora(leitura_anterior, leitura_atual)
    if qtd_pioras >= 2:
        nivel_antes_e2 = estado["nivel"]
        novo_nivel = max(1, nivel_antes_e2 - 1)
        estado["nivel"] = novo_nivel
        estado["proxima_leitura_minutos"] = 5
        eventos.append(
            f"E2: {qtd_pioras} sinais pioraram simultaneamente — "
            f"nível elevado {nivel_antes_e2} → {novo_nivel}, nova leitura em 5 min"
        )

    # --- E3: paciente aguarda além do SLA ---
    sla = SLA_POR_NIVEL.get(estado["nivel"], 999)
    hora_entrada = paciente.get("hora_entrada", leitura_anterior["hora"])
    minutos_espera = _parse_hora(leitura_atual["hora"]) - _parse_hora(hora_entrada)

    if minutos_espera > sla:
        estado["violacoes_sla"] = estado.get("violacoes_sla", 0) + 1
        eventos.append(
            f"E3: violação de SLA — paciente aguarda {minutos_espera} min "
            f"(limite Nível {estado['nivel']}: {sla} min) — supervisor alertado"
        )

        # --- E5: segunda violação de SLA ---
        if estado["violacoes_sla"] >= 2:
            eventos.append(
                f"E5: dupla violação de SLA detectada — "
                f"novas admissões bloqueadas, protocolo de sobrecarga acionado"
            )

    # --- E4: vulnerável + temperatura subiu > 1°C → força exatamente Nível 2 ---
    # CORRIGIDO: E4 não rebaixa quem já está em Nível 1 (mais urgente).
    # Antes, E4 usava min(nivel, 2) que podia conflitar com E2 que já tinha
    # elevado para 1. Agora aplica apenas se o nível atual for > 2.
    eh_vulneravel = (
        paciente.get("idade", 0) >= 60
        or paciente.get("gestante", False)
        or paciente.get("deficiencia", False)
    )
    temp_ant = leitura_anterior.get("temperatura")
    temp_atu = leitura_atual.get("temperatura")

    if eh_vulneravel and temp_ant is not None and temp_atu is not None:
        if temp_atu - temp_ant > 1.0:
            # E4 força no máximo Nível 2 — não rebaixa quem já está em Nível 1
            if estado["nivel"] > 2:
                estado["nivel"] = 2
            eventos.append(
                f"E4: paciente vulnerável com temperatura subindo "
                f"{temp_ant}°C → {temp_atu}°C (+{temp_atu - temp_ant:.1f}°C) "
                f"— confirmado Nível 2 (regra E4)"
            )

    return eventos


# ---------------------------------------------------------------------------
# Ponto de entrada principal
# CORRIGIDO: ordem correta — primária → vulnerabilidade → segunda ordem.
# Antes, main.py chamava segunda ordem antes de atualizar estado["nivel"].
# ---------------------------------------------------------------------------

def processar(paciente):
    """
    Processa todas as leituras e retorna:
      - nivel_atual
      - historico_niveis: lista de (hora, nivel) a cada mudança
      - eventos: todas as regras de 2ª ordem que dispararam
      - alertas: subset com E3 e E5
    """
    estado = {
        "nivel": None,
        "nivel_anterior": None,
        "violacoes_sla": 0,
        "proxima_leitura_minutos": None,
    }
    historico_niveis = []
    todos_eventos = []

    leituras = paciente.get("leituras", [])

    for i, leitura in enumerate(leituras):

        # 1. Classificação primária
        novo_nivel = aplicar_regras(leitura)

        if novo_nivel is not None:
            if estado["nivel"] is None or novo_nivel < estado["nivel"]:
                estado["nivel_anterior"] = estado["nivel"]
                estado["nivel"] = novo_nivel
                historico_niveis.append((leitura["hora"], estado["nivel"]))

        # 2. Regra de vulnerabilidade
        if estado["nivel"] is not None:
            nivel_com_vuln = _ajustar_vulnerabilidade(estado["nivel"], paciente)
            if nivel_com_vuln < estado["nivel"]:
                estado["nivel_anterior"] = estado["nivel"]
                estado["nivel"] = nivel_com_vuln
                historico_niveis.append((leitura["hora"], estado["nivel"]))

        # 3. Regras de segunda ordem (a partir da 2ª leitura)
        if i > 0 and estado["nivel"] is not None:
            eventos = aplicar_regras_segunda_ordem(
                estado, leituras[i - 1], leitura, paciente
            )
            todos_eventos.extend(eventos)
            # Se segunda ordem mudou o nível, registra no histórico
            ultimo_hist = historico_niveis[-1][1] if historico_niveis else None
            if estado["nivel"] != ultimo_hist:
                historico_niveis.append((leitura["hora"], estado["nivel"]))

    alertas = [e for e in todos_eventos if "E3:" in e or "E5:" in e]

    return {
        "nivel_atual": estado["nivel"],
        "historico_niveis": historico_niveis,
        "eventos": todos_eventos,
        "alertas": alertas,
    }


# Compatibilidade com testes que instanciam MotorInferencia()
class MotorInferencia:
    def processar(self, paciente):
        return processar(paciente)