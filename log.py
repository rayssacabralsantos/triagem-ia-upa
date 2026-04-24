# Módulo de log auditável
#
# BUG CORRIGIDO: mostrar_log tinha indentação misturada (tab + espaços),
# causando IndentationError em alguns interpretadores.
#
# MELHORIA: log encapsulado em classe para evitar estado global compartilhado
# entre importações — o log antigo era uma lista global que acumulava entradas
# de execuções anteriores se o módulo fosse reimportado no mesmo processo.

import json
from datetime import datetime


class Log:
    def __init__(self):
        self._entradas = []

    def registrar(self, hora, regra, entrada, saida):
        self._entradas.append({
            "hora": hora,
            "regra": regra,
            "entrada": entrada,
            "saida": saida,
        })

    def mostrar(self):
        for entrada in self._entradas:
            print(
                f"[{entrada['hora']}] {entrada['regra']} → {entrada['saida']}"
            )

    def exportar(self):
        return list(self._entradas)

    def limpar(self):
        self._entradas = []


# Instância global padrão — usada pelo main.py via 'from log import registrar'
_log_global = Log()


def registrar(hora, regra, entrada, saida):
    _log_global.registrar(hora, regra, entrada, saida)


def mostrar_log():
    _log_global.mostrar()


def exportar_log():
    return _log_global.exportar()