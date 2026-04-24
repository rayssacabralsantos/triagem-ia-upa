"""
Suite de Testes — Sistema de Triagem Inteligente para UPA (SUS Brasil)
Disciplina: Inteligência Artificial — J903 / 2026

Cobre obrigatoriamente:
  - Os cinco cenários de empate (E1 a E5)
  - Pelo menos dois cenários com piora progressiva ao longo do tempo
  - Um cenário com violação dupla de SLA (regra E5)
  - Um cenário com paciente vulnerável e piora de temperatura (regra E4)

Total: 12 cenários de teste.
"""

import unittest
import sys
import os

# Ajusta o path para importar os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor_inferencia import MotorInferencia
from desempate import ModuloDesempate

# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------

def criar_paciente(
    id_pac,
    idade=30,
    gestante=False,
    deficiencia=False,
    hora_entrada="10:00",
    leituras=None,
):
    return {
        "id": id_pac,
        "idade": idade,
        "gestante": gestante,
        "deficiencia": deficiencia,
        "hora_entrada": hora_entrada,
        "leituras": leituras or [],
    }


def leitura(
    hora,
    consciente=True,
    glasgow=15,
    spo2=97,
    frequencia_cardiaca=80,
    temperatura=36.8,
    escala_dor=0,
    vomitos_por_hora=0,
    pulso_presente=True,
    respirando=True,
):
    return {
        "hora": hora,
        "consciente": consciente,
        "glasgow": glasgow,
        "spo2": spo2,
        "frequencia_cardiaca": frequencia_cardiaca,
        "temperatura": temperatura,
        "escala_dor": escala_dor,
        "vomitos_por_hora": vomitos_por_hora,
        "pulso_presente": pulso_presente,
        "respirando": respirando,
    }


# ---------------------------------------------------------------------------
# Classe de testes
# ---------------------------------------------------------------------------

class TestTriagemUPA(unittest.TestCase):
    def setUp(self):
        self.motor = MotorInferencia()
        self.desempate = ModuloDesempate()

    # =======================================================================
    # CENÁRIO 1 — Classificação básica: paciente Nível 1 (emergência)
    # Cobre: regra primária Nível 1 (parada cardiorrespiratória)
    # =======================================================================
    def test_01_nivel1_emergencia(self):
        """
        Paciente sem pulso e em apneia deve ser classificado como Nível 1
        imediatamente, independentemente de qualquer outro sinal vital.
        """
        pac = criar_paciente(
            "PAC-001",
            idade=45,
            hora_entrada="08:00",
            leituras=[
                leitura("08:00", pulso_presente=False, respirando=False,
                        glasgow=3, spo2=70)
            ],
        )
        resultado = self.motor.processar(pac)
        self.assertEqual(resultado["nivel_atual"], 1,
                         "Parada cardiorrespiratória deve ser Nível 1")
        self.assertIn("1", str(resultado["nivel_atual"]))

    # =======================================================================
    # CENÁRIO 2 — Classificação básica: paciente Nível 4 (pouco urgente)
    # Cobre: regra primária Nível 4
    # =======================================================================
    def test_02_nivel4_pouco_urgente(self):
        """
        Paciente com dor leve (2/10) e sinais estáveis deve ser classificado
        como Nível 4.
        """
        pac = criar_paciente(
            "PAC-002",
            idade=28,
            hora_entrada="09:00",
            leituras=[
                leitura("09:00", escala_dor=2, spo2=98,
                        frequencia_cardiaca=72, temperatura=36.5)
            ],
        )
        resultado = self.motor.processar(pac)
        self.assertEqual(resultado["nivel_atual"], 4,
                         "Dor leve com sinais estáveis deve ser Nível 4")

    # =======================================================================
    # CENÁRIO 3 — Piora progressiva ao longo do tempo (1ª ocorrência)
    # Cobre: encadeamento E1 e E2; requisito "pelo menos dois com piora progressiva"
    # =======================================================================
    def test_03_piora_progressiva_nivel3_para_2(self):
        """
        Paciente inicia em Nível 3 e, em menos de 30 minutos, dois sinais
        vitais pioram simultaneamente (SpO2 e FC), disparando E2 (elevação de
        prioridade) e E1 (notificação de reclassificação crítica).
        """
        pac = criar_paciente(
            "PAC-003",
            idade=40,
            hora_entrada="10:00",
            leituras=[
                # Leitura inicial: Nível 3 (febre + dor 6)
                leitura("10:00", temperatura=39.5, escala_dor=6,
                        spo2=94, frequencia_cardiaca=100),
                # 20 min depois: SpO2 cai abaixo de 90% e FC > 150 (dois sinais)
                leitura("10:20", temperatura=39.5, escala_dor=6,
                        spo2=88, frequencia_cardiaca=155),
            ],
        )
        resultado = self.motor.processar(pac)
        # Nível deve ter subido para 2 (ou 1)
        self.assertLessEqual(resultado["nivel_atual"], 2,
                             "Dois sinais piorando devem elevar para Nível 2")
        # Regra E1 deve ter sido disparada (reclassificação em < 30 min)
        self.assertTrue(
            any("E1" in str(e) or "critico" in str(e).lower()
                for e in resultado.get("eventos", [])),
            "Reclassificação em < 30 min deve registrar evento crítico (E1)",
        )

    # =======================================================================
    # CENÁRIO 4 — Piora progressiva ao longo do tempo (2ª ocorrência)
    # Cobre: requisito "pelo menos dois com piora progressiva"
    # =======================================================================
    def test_04_piora_progressiva_multiplas_leituras(self):
        """
        Paciente tem três leituras com deterioração gradual e contínua de SpO2
        e Glasgow, acumulando elevações de prioridade a cada rodada de
        encadeamento.
        """
        pac = criar_paciente(
            "PAC-004",
            idade=55,
            hora_entrada="11:00",
            leituras=[
                leitura("11:00", spo2=95, glasgow=15, escala_dor=4,
                        frequencia_cardiaca=90),   # Nível 4
                leitura("11:20", spo2=93, glasgow=14, escala_dor=6,
                        frequencia_cardiaca=125),  # Nível 3 → E2 dispara
                leitura("11:40", spo2=88, glasgow=13, escala_dor=8,
                        frequencia_cardiaca=155),  # Nível 2
            ],
        )
        resultado = self.motor.processar(pac)
        nivel_final = resultado["nivel_atual"]
        self.assertLessEqual(nivel_final, 2,
                             "Deterioração progressiva deve atingir Nível 2 ou superior")
        # Histórico de classificações deve conter pelo menos 2 escaladas
        historico = resultado.get("historico_niveis", [])
        self.assertGreaterEqual(len(historico), 2,
                                "Deve haver pelo menos 2 mudanças de nível no histórico")

    # =======================================================================
    # CENÁRIO 5 — Paciente vulnerável + piora de temperatura (regra E4)
    # Cobre: requisito obrigatório "um com paciente vulnerável e piora de temp"
    # =======================================================================
    def test_05_vulneravel_piora_temperatura_regra_E4(self):
        """
        Paciente com 68 anos (vulnerável) tem temperatura elevada em 1,5 °C
        entre leituras. Regra E4 deve reclassificá-lo diretamente para Nível 2,
        independentemente do nível clinicamente calculado.
        """
        pac = criar_paciente(
            "PAC-005",
            idade=68,          # vulnerável: >= 60 anos
            hora_entrada="12:00",
            leituras=[
                leitura("12:00", temperatura=37.8, spo2=96,
                        frequencia_cardiaca=85, escala_dor=3),  # Nível 4 clínico
                leitura("12:15", temperatura=39.4, spo2=96,
                        frequencia_cardiaca=85, escala_dor=3),  # +1,6 °C → E4
            ],
        )
        resultado = self.motor.processar(pac)
        self.assertEqual(resultado["nivel_atual"], 2,
                         "Regra E4: vulnerável + piora de temp. deve ir a Nível 2")
        self.assertTrue(
            any("E4" in str(e) for e in resultado.get("eventos", [])),
            "Evento E4 deve constar no log de inferências",
        )

    # =======================================================================
    # CENÁRIO 6 — Violação dupla de SLA (regra E5)
    # Cobre: requisito obrigatório "um com violação dupla de SLA"
    # =======================================================================
    def test_06_violacao_dupla_sla_regra_E5(self):
        """
        Paciente Nível 3 aguarda além de 30 min (1ª violação → E3) e,
        sem atendimento, extrapola novamente (2ª violação → E5 deve bloquear
        novas admissões e acionar protocolo de sobrecarga).
        """
        pac = criar_paciente(
            "PAC-006",
            idade=35,
            hora_entrada="07:00",
            leituras=[
                leitura("07:00", temperatura=39.8, escala_dor=6),  # Nível 3
                leitura("07:35", temperatura=39.8, escala_dor=6),  # +35 min → 1ª violação E3
                leitura("08:10", temperatura=39.8, escala_dor=6),  # +70 min → 2ª violação → E5
            ],
        )
        resultado = self.motor.processar(pac)
        alertas = resultado.get("alertas", [])
        self.assertTrue(
            any("E5" in str(a) or "sobrecarga" in str(a).lower()
                or "bloqueio" in str(a).lower() for a in alertas),
            "Dupla violação de SLA deve disparar protocolo de sobrecarga (E5)",
        )
        # Deve haver ao menos 2 alertas de violação para o mesmo paciente
        violacoes = [a for a in alertas
                     if "violacao" in str(a).lower() or "E3" in str(a)]
        self.assertGreaterEqual(len(violacoes), 2,
                                "Deve haver 2 alertas de violação de SLA (E3) antes de E5")

    # =======================================================================
    # CENÁRIOS DE EMPATE — obrigatórios (E1 a E5 da Seção 3)
    # =======================================================================

    # EMPATE 1 — Mesmo nível, mesma hora de chegada, nenhum vulnerável
    def test_07_empate1_mesmo_nivel_mesma_hora(self):
        """
        Dois pacientes no Nível 3 chegaram com diferença < 1 minuto.
        Nenhum é vulnerável. O critério de desempate deve ser determinístico
        e auditável (ex.: ordem de registro interno, sorteia semente fixa).
        """
        pac_a = criar_paciente(
            "PAC-007A", idade=30, hora_entrada="13:00",
            leituras=[leitura("13:00", temperatura=39.5, escala_dor=6)]
        )
        pac_b = criar_paciente(
            "PAC-007B", idade=25, hora_entrada="13:00",
            leituras=[leitura("13:00", temperatura=39.2, escala_dor=5)]
        )
        r_a = self.motor.processar(pac_a)
        r_b = self.motor.processar(pac_b)
        self.assertEqual(r_a["nivel_atual"], 3)
        self.assertEqual(r_b["nivel_atual"], 3)

        ordem = self.desempate.resolver([pac_a, pac_b], [r_a, r_b])
        # Deve retornar exatamente um paciente à frente
        self.assertEqual(len(ordem), 2, "Desempate deve retornar os 2 pacientes ordenados")
        self.assertNotEqual(ordem[0]["id"], ordem[1]["id"])
        # Determinismo: segunda chamada deve dar a mesma ordem
        ordem2 = self.desempate.resolver([pac_a, pac_b], [r_a, r_b])
        self.assertEqual(ordem[0]["id"], ordem2[0]["id"],
                         "O critério de desempate deve ser determinístico")

    # EMPATE 2 — Mesmo nível, velocidade de piora diferente
    def test_08_empate2_velocidade_de_piora(self):
        """
        Paciente A: Nível 3 há 25 min, estável.
        Paciente B: Nível 3 há 5 min, mas dois sinais vitais pioraram na 2ª leitura.
        B deve ter prioridade sobre A (piora objetiva pesa mais que tempo de espera
        quando ainda dentro do SLA).
        """
        pac_a = criar_paciente(
            "PAC-008A", idade=40, hora_entrada="14:00",
            leituras=[
                leitura("14:00", temperatura=39.5, escala_dor=6),
                leitura("14:25", temperatura=39.5, escala_dor=6),   # estável
            ]
        )
        pac_b = criar_paciente(
            "PAC-008B", idade=35, hora_entrada="14:20",
            leituras=[
                leitura("14:20", temperatura=39.2, escala_dor=5),
                leitura("14:25", temperatura=39.2, escala_dor=5,    # 2 sinais piores
                        frequencia_cardiaca=148, spo2=91),
            ]
        )
        r_a = self.motor.processar(pac_a)
        r_b = self.motor.processar(pac_b)
        self.assertEqual(r_a["nivel_atual"], 3)

        ordem = self.desempate.resolver([pac_a, pac_b], [r_a, r_b])
        self.assertEqual(ordem[0]["id"], "PAC-008B",
                         "Piora clínica objetiva recente deve priorizar B sobre A")

    # EMPATE 3 — Vulnerável vs. piora clínica objetiva
    def test_09_empate3_vulneravel_vs_piora_clinica(self):
        """
        A: 62 anos, Nível 3 por vulnerabilidade, aguardando 28 min.
        B: 35 anos, Nível 3 clínico, SpO2 caiu 3 pontos na última leitura.
        O critério deve ponderar risco objetivo; o resultado deve ser auditável.
        """
        pac_a = criar_paciente(
            "PAC-009A", idade=62, hora_entrada="15:00",
            leituras=[
                leitura("15:00", escala_dor=3, spo2=96),
                leitura("15:28", escala_dor=3, spo2=96),   # estável, já 28 min
            ]
        )
        pac_b = criar_paciente(
            "PAC-009B", idade=35, hora_entrada="15:15",
            leituras=[
                leitura("15:15", escala_dor=5, spo2=95),
                leitura("15:28", escala_dor=5, spo2=92),   # SpO2 caiu 3 pts
            ]
        )
        r_a = self.motor.processar(pac_a)
        r_b = self.motor.processar(pac_b)

        ordem = self.desempate.resolver([pac_a, pac_b], [r_a, r_b])
        self.assertEqual(len(ordem), 2)
        # Log de desempate deve justificar a decisão
        log = self.desempate.ultimo_log()
        self.assertIsNotNone(log, "O módulo de desempate deve gerar log auditável")
        self.assertTrue(len(log) > 0, "Log de desempate não pode estar vazio")

    # EMPATE 4 — Violação de SLA iminente simultânea
    def test_10_empate4_sla_iminente_simultaneo(self):
        """
        Dois pacientes no Nível 3 vão violar o SLA em ≈ 2 minutos ao mesmo
        tempo. Apenas uma sala disponível. O sistema deve escalar os dois (E3)
        e escolher um, documentando o critério.
        """
        pac_a = criar_paciente(
            "PAC-010A", idade=30, hora_entrada="16:00",
            leituras=[
                leitura("16:00", temperatura=39.5, escala_dor=6),
                leitura("16:31", temperatura=39.5, escala_dor=6),   # 31 min → viola SLA de 30 min
            ]
        )
        pac_b = criar_paciente(
            "PAC-010B", idade=28, hora_entrada="16:00",
            leituras=[
                leitura("16:00", temperatura=39.1, escala_dor=5),
                leitura("16:31", temperatura=39.1, escala_dor=5),   # idem
            ]
        )
        r_a = self.motor.processar(pac_a)
        r_b = self.motor.processar(pac_b)

        alertas_a = r_a.get("alertas", [])
        alertas_b = r_b.get("alertas", [])
        # Ambos devem ter recebido alerta de violação iminente (E3)
        self.assertTrue(
            any("E3" in str(al) or "violacao" in str(al).lower() for al in alertas_a),
            "PAC-010A deve receber alerta de violação de SLA (E3)",
        )
        self.assertTrue(
            any("E3" in str(al) or "violacao" in str(al).lower() for al in alertas_b),
            "PAC-010B deve receber alerta de violação de SLA (E3)",
        )
        # Desempate deve escolher um e justificar
        ordem = self.desempate.resolver([pac_a, pac_b], [r_a, r_b])
        self.assertEqual(len(ordem), 2)

    # EMPATE 5 — Empate após reclassificação
    def test_11_empate5_recem_reclassificado_vs_antigo(self):
        """
        Paciente A: acabou de subir de Nível 4 para Nível 3 agora.
        Paciente B: está no Nível 3 há 15 min.
        Para fins de fila, o tempo de espera no nível atual é o critério:
        B deve vir primeiro (entrou no nível antes de A).
        """
        pac_a = criar_paciente(
            "PAC-011A", idade=32, hora_entrada="17:00",
            leituras=[
                leitura("17:00", escala_dor=2, spo2=98),   # Nível 4
                leitura("17:30", escala_dor=6, temperatura=36.8, spo2=98),  # só dor mudou, nível 3
            ]
        )
        pac_b = criar_paciente(
            "PAC-011B", idade=29, hora_entrada="17:00",
            leituras=[
                leitura("17:00", escala_dor=6, temperatura=39.6),   # Nível 3 desde 17:00
                leitura("17:15", escala_dor=6, temperatura=39.6),
            ]
        )
        r_a = self.motor.processar(pac_a)
        r_b = self.motor.processar(pac_b)
        self.assertEqual(r_a["nivel_atual"], 3)
        self.assertEqual(r_b["nivel_atual"], 3)

        ordem = self.desempate.resolver([pac_a, pac_b], [r_a, r_b])
        self.assertEqual(ordem[0]["id"], "PAC-011B",
                         "B está no Nível 3 há mais tempo e deve ser atendido primeiro")

    # =======================================================================
    # CENÁRIO 12 — Segurança: rebaixamento automático proibido
    # Cobre: restrição de segurança do enunciado
    # =======================================================================
    def test_12_rebaixamento_automatico_proibido(self):
        """
        Mesmo que os sinais vitais melhorem entre leituras, o sistema NUNCA
        deve reduzir automaticamente o nível de prioridade. Rebaixamentos
        exigem confirmação manual.
        """
        pac = criar_paciente(
            "PAC-012",
            idade=40,
            hora_entrada="18:00",
            leituras=[
                leitura("18:00", spo2=88, frequencia_cardiaca=155,
                        escala_dor=9),   # Nível 2 (SpO2 < 90% e FC > 150)
                leitura("18:20", spo2=96, frequencia_cardiaca=90,
                        escala_dor=4),   # sinais voltaram ao normal
            ],
        )
        resultado = self.motor.processar(pac)
        # O nível não pode ter diminuído para 3, 4 ou 5
        self.assertLessEqual(resultado["nivel_atual"], 2,
                             "Sistema não pode rebaixar automaticamente: nível deve ser ≤ 2")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)