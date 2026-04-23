log = []

def registrar(hora, regra, entrada, saida):
    log.append({
        "hora": hora,
        "regra": regra,
        "entrada": entrada,
        "saida": saida
    })

def mostrar_log():
        for l in log:
            print(l)