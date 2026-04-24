# Regras primárias — Protocolo de Manchester (adaptação SUS)
# Representadas como dados: lista de dicionários com condições e ação.
# O motor avalia cada regra e aplica o nível mais urgente encontrado.
#
# BUG CORRIGIDO: a regra de Emergência usava AND entre pulso e respiração,
# mas a ausência de qualquer um dos dois já configura emergência (OR).
# Solução: duas regras separadas de nível 1, uma para cada condição.
#
# ADICIONADO: condições completas do protocolo para níveis 2 e 3
# (Glasgow, FC extrema, dor 5-7, vômitos) que estavam ausentes.

regras = [
    # ----- Nível 1 — Emergência -----
    {
        "nome": "Emergência - sem pulso",
        "condicoes": [
            {"campo": "pulso_presente", "op": "==", "valor": False}
        ],
        "acao": {"nivel": 1}
    },
    {
        "nome": "Emergência - apneia",
        "condicoes": [
            {"campo": "respirando", "op": "==", "valor": False}
        ],
        "acao": {"nivel": 1}
    },

    # ----- Nível 2 — Muito urgente -----
    {
        "nome": "Muito urgente - SpO2 baixa",
        "condicoes": [
            {"campo": "spo2", "op": "<", "valor": 90}
        ],
        "acao": {"nivel": 2}
    },
    {
        "nome": "Muito urgente - dor intensa",
        "condicoes": [
            {"campo": "escala_dor", "op": ">=", "valor": 8}
        ],
        "acao": {"nivel": 2}
    },
    {
        "nome": "Muito urgente - Glasgow baixo",
        "condicoes": [
            {"campo": "glasgow", "op": "<", "valor": 14}
        ],
        "acao": {"nivel": 2}
    },
    {
        "nome": "Muito urgente - FC muito alta",
        "condicoes": [
            {"campo": "frequencia_cardiaca", "op": ">", "valor": 150}
        ],
        "acao": {"nivel": 2}
    },
    {
        "nome": "Muito urgente - FC muito baixa",
        "condicoes": [
            {"campo": "frequencia_cardiaca", "op": "<", "valor": 40}
        ],
        "acao": {"nivel": 2}
    },

    # ----- Nível 3 — Urgente -----
    {
        "nome": "Urgente - febre alta",
        "condicoes": [
            {"campo": "temperatura", "op": ">", "valor": 39}
        ],
        "acao": {"nivel": 3}
    },
    {
        "nome": "Urgente - dor moderada",
        "condicoes": [
            {"campo": "escala_dor", "op": ">=", "valor": 5},
            {"campo": "escala_dor", "op": "<=", "valor": 7}
        ],
        "acao": {"nivel": 3}
    },
    {
        "nome": "Urgente - vômitos frequentes",
        "condicoes": [
            {"campo": "vomitos_por_hora", "op": ">", "valor": 3}
        ],
        "acao": {"nivel": 3}
    },
    {
        "nome": "Urgente - FC elevada",
        "condicoes": [
            {"campo": "frequencia_cardiaca", "op": ">=", "valor": 120},
            {"campo": "frequencia_cardiaca", "op": "<=", "valor": 150}
        ],
        "acao": {"nivel": 3}
    },
    {
        "nome": "Urgente - FC baixa",
        "condicoes": [
            {"campo": "frequencia_cardiaca", "op": ">=", "valor": 40},
            {"campo": "frequencia_cardiaca", "op": "<=", "valor": 50}
        ],
        "acao": {"nivel": 3}
    },

    # ----- Nível 4 — Pouco urgente -----
    {
        "nome": "Pouco urgente - dor leve",
        "condicoes": [
            {"campo": "escala_dor", "op": ">=", "valor": 1},
            {"campo": "escala_dor", "op": "<=", "valor": 4}
        ],
        "acao": {"nivel": 4}
    },

    # ----- Nível 5 — Não urgente -----
    {
        "nome": "Não urgente - sem dor",
        "condicoes": [
            {"campo": "escala_dor", "op": "==", "valor": 0}
        ],
        "acao": {"nivel": 5}
    },
]

# SLAs por nível (em minutos) — usados pelas regras E3/E5
SLA_POR_NIVEL = {
    1: 0,
    2: 10,
    3: 30,
    4: 60,
    5: 120,
}