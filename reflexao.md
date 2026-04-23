## Reflexão
O sistema desenvolvido utiliza encadeamento progressivo para classificar pacientes, com base em sinais vitais, respeitando as regras do Protocolo de Manchester e priorizando situações de maior risco clínico.

O critério de desempate foi baseado em um score que considera tempo de espera, gravidade e piora recente do quadro clínico. Essa abordagem permite decisões determinísticas e auditáveis, garantindo que o mesmo cenário produza sempre o mesmo resultado.

Em situações de alta demanda, como uma UPA com grande quantidade de pacientes no nível 3, o sistema se mantém consistente, priorizando aqueles com maior risco ou maior tempo de espera. No entanto, pode haver conflitos entre pacientes com longa espera e pacientes com piora clínica recente, exigindo um balanceamento cuidadoso dos pesos utilizados no cálculo do score.

Uma limitação do sistema é a dependência da qualidade e frequência das leituras de sinais vitais. Dados incompletos ou desatualizados podem implicar diretamente a decisão final.

Em relação à equidade, o sistema não utiliza atributos sensíveis como genêro, raça ou condição socioêconomica, evitando vieses discriminatórios. A única execão é a priorização de grupos vulneráveis, conforme definido pelas regras do SUS.

Por fim, o sistema demonstra ser eficaz na priorização automatizada, porém ainda depende de supervisão humana em casos críticos, especialmente quando há necessidade de reavaliação clínica mais complexa.