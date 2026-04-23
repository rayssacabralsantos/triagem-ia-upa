from desempate import ordenar_pacientes

pacientes = [
    {"id": "A", "nivel": 3, "tempo_espera": 25, "piora": 0},
    {"id": "B", "nivel": 3, "tempo_espera": 5, "piora": 2},
]

ordenados = ordenar_pacientes(pacientes)

for p in ordenados:
    print(p)