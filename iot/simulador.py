import random
import time
from prometheus_client import Counter, Gauge, start_http_server

# Metricas que o Prometheus vai coletar
sucessos = Counter(
    "mecaniqa_leituras_sucesso_total",
    "Quantidade de leituras IoT processadas com sucesso"
)

erros = Counter(
    "mecaniqa_leituras_erro_total",
    "Quantidade de leituras IoT com erro"
)

temperatura_motor = Gauge(
    "mecaniqa_temperatura_motor_celsius",
    "Temperatura atual do motor em Celsius"
)

# Disponibiliza as metricas na porta 8000
start_http_server(8000)

print("Simulador IoT MecaniQA iniciado!")
print("Metricas disponiveis em http://localhost:8000/metrics")

while True:
    temperatura = round(random.uniform(65, 115), 1)
    falha_eletrica = random.random() < 0.05

    temperatura_motor.set(temperatura)

    if temperatura > 105 or falha_eletrica:
        erros.inc()
        print(f"ERRO - Temperatura: {temperatura} C")
    else:
        sucessos.inc()
        print(f"SUCESSO - Temperatura: {temperatura} C")

    time.sleep(2)
