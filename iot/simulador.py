import hashlib
import json
import random
import threading
import time

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from prometheus_client import Counter, Gauge, start_http_server


# METRICAS PROMETHEUS

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


# PROCESSAMENTO DAS LEITURAS

def processar_leitura(temperatura, falha_eletrica):
    temperatura_motor.set(temperatura)

    if temperatura > 105 or falha_eletrica:
        erros.inc()
        return "erro"

    sucessos.inc()
    return "sucesso"


# RECEBIMENTO DE LEITURAS VIA HTTP

class LeituraHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/leitura":
            self.responder(404, {"erro": "Endpoint nao encontrado"})
            return

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))

            if tamanho <= 0 or tamanho > 2048:
                raise ValueError("Tamanho de requisicao invalido")

            dados = json.loads(self.rfile.read(tamanho))

            temperatura = float(dados["temperatura"])
            falha_eletrica = dados.get("falha_eletrica", False)

            if not isinstance(falha_eletrica, bool):
                raise ValueError("Falha eletrica deve ser booleana")

        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.responder(400, {"erro": "Leitura invalida"})
            return

        # Simula processamento computacional do sensor.
        # Esta operacao gera consumo real de CPU.
        hashlib.pbkdf2_hmac(
            "sha256",
            b"mecaniqa",
            b"sensor-iot",
            30000
        )

        resultado = processar_leitura(
            temperatura,
            falha_eletrica
        )

        self.responder(200, {"resultado": resultado})

    def responder(self, codigo, dados):
        resposta = json.dumps(dados).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resposta)))
        self.end_headers()

        self.wfile.write(resposta)

    def log_message(self, formato, *args):
        pass


# SERVIDORES HTTP

start_http_server(8000)

servidor_iot = ThreadingHTTPServer(
    ("0.0.0.0", 8001),
    LeituraHandler
)

threading.Thread(
    target=servidor_iot.serve_forever,
    daemon=True
).start()

print("Simulador IoT MecaniQA iniciado!", flush=True)
print("Prometheus: porta 8000/metrics", flush=True)
print("Leituras IoT: porta 8001/leitura", flush=True)


# SIMULACAO AUTOMATICA ORIGINAL

while True:
    temperatura = round(random.uniform(65, 115), 1)
    falha_eletrica = random.random() < 0.05

    resultado = processar_leitura(
        temperatura,
        falha_eletrica
    )

    print(
        f"{resultado.upper()} - Temperatura: {temperatura} C",
        flush=True
    )

    time.sleep(2)
