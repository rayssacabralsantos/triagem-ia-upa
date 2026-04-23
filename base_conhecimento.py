regras = [
    {
        "nome": "Emergência",
        "condicoes": [
            {"campo": "pulso_presente", "op": "==", "valor": False},
            {"campo": "respirando", "op": "==", "valor": False}
        ],
        "acao": {"nivel": 1}
    },
    {
        "nome": "Muito urgente",
        "condicoes": [
            {"campo": "spo2", "op": "<", "valor": 90}
        ],
        "acao": {"nivel": 2}
    },
    {
        "nome": "Urgente",
        "condicoes": [
            {"campo": "temperatura", "op": ">", "valor": 39}
        ],
        "acao": {"nivel": 3}
    },
    {
        "nome": "Pouco urgente",
        "condicoes": [
            {"campo": "escala_dor", "op": "<=", "valor": 4}
        ],
        "acao": {"nivel": 4}
    },
    {
        "nome": "Não urgente",
        "condicoes": [
            {"campo": "escala_dor", "op": "==", "valor": 0}
        ],
        "acao": {"nivel": 5}
    }
]