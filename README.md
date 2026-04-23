# Sistema de Triagem Inteligente - UPA (SUS)

Projeto desenvolvido para a disciplina de Inteligência Artificial.

# Integrantes
Integrante 1: Rayssa Cabral Santos              |  RA: F3581G3
Integrante 2: Carlos Eduardo M. M. M. Benigin   |  RA: G030BI5
Integrante 3: Isabella Bonjani Gonçalves         |  RA: R091HF0


## 📌 Descrição
Sistema especialista com encadeamento progressivo (foward chaining) para classificação de pacientes com base no Protocolo de Manchester.

## ⚖️ Critério de Desempate

O sistema utiliza um score baseado em:
- tempo de espera
- gravidade (nível)
- piora clínica recente

Pacientes com maior score são executados

## ⚙️ Como executar

No terminal:

```bash
python main.py
