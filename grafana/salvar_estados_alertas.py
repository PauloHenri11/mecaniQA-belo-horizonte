import base64
import getpass
import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

usuario = input("Usuario Grafana [admin]: ").strip() or "admin"
senha = getpass.getpass("Senha Grafana: ")

token = base64.b64encode(
    f"{usuario}:{senha}".encode()
).decode()

requisicao = Request(
    "http://localhost:3000/api/prometheus/grafana/api/v1/rules",
    headers={"Authorization": f"Basic {token}"}
)

with urlopen(requisicao, timeout=20) as resposta:
    dados = json.load(resposta)

pasta = Path("evidencias/oat2/21-10")
pasta.mkdir(parents=True, exist_ok=True)

arquivo = pasta / f"08-alertas-{datetime.now():%H%M%S}.json"

arquivo.write_text(
    json.dumps(dados, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("\nEVIDENCIA SALVA:", arquivo)

for grupo in dados.get("data", {}).get("groups", []):
    for regra in grupo.get("rules", []):
        nome = regra.get("name", "")
        if "OAT2" in nome:
            print(nome, "=>", regra.get("state", "indisponivel"))
