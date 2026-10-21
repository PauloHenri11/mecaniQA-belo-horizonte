import base64
import getpass
import json
from pathlib import Path
from urllib import request, error

BASE = "http://localhost:3000"

usuario = input("Usuario Grafana [admin]: ").strip() or "admin"
senha = getpass.getpass("Senha Grafana: ")

credenciais = base64.b64encode(
    f"{usuario}:{senha}".encode()
).decode()

HEADERS = {
    "Authorization": f"Basic {credenciais}",
    "Content-Type": "application/json",
    "X-Disable-Provenance": "true"
}


def api(metodo, caminho, dados=None):
    corpo = json.dumps(dados).encode() if dados is not None else None

    req = request.Request(
        BASE + caminho,
        data=corpo,
        headers=HEADERS,
        method=metodo
    )

    try:
        with request.urlopen(req, timeout=20) as resposta:
            texto = resposta.read()
            return json.loads(texto) if texto else {}

    except error.HTTPError as exc:
        if exc.code == 404 and metodo == "GET":
            return None

        raise SystemExit(
            f"Erro HTTP {exc.code}: {exc.read().decode()[:500]}"
        )

    except error.URLError as exc:
        raise SystemExit(f"Grafana inacessivel: {exc}")


# Localizar a fonte Prometheus
fontes = api("GET", "/api/datasources")

prometheus = next(
    (f for f in fontes if f["type"] == "prometheus"),
    None
)

if not prometheus:
    raise SystemExit("Fonte Prometheus nao encontrada no Grafana.")

fonte_uid = prometheus["uid"]
pasta_uid = "mecaniqa-oat2"

# Criar pasta para os alertas
if not api("GET", f"/api/folders/{pasta_uid}"):
    api("POST", "/api/folders", {
        "uid": pasta_uid,
        "title": "MecaniQA - OAT 2"
    })


def criar_alerta(uid, titulo, consulta, comparacao, limite, duracao):
    if api("GET", f"/api/v1/provisioning/alert-rules/{uid}"):
        print(f"JA EXISTE: {titulo}")
        return

    regra = {
        "uid": uid,
        "title": titulo,
        "orgId": 1,
        "folderUID": pasta_uid,
        "ruleGroup": "Monitoramento IoT",
        "condition": "B",
        "for": duracao,
        "noDataState": "Alerting" if uid == "mqiotok" else "NoData",
        "execErrState": "Error",
        "isPaused": False,
        "annotations": {
            "summary": titulo
        },
        "labels": {
            "projeto": "mecaniqa"
        },
        "data": [
            {
                "refId": "A",
                "queryType": "",
                "relativeTimeRange": {
                    "from": 120,
                    "to": 0
                },
                "datasourceUid": fonte_uid,
                "model": {
                    "expr": consulta,
                    "editorMode": "code",
                    "instant": True,
                    "range": False,
                    "refId": "A",
                    "intervalMs": 1000,
                    "maxDataPoints": 43200
                }
            },
            {
                "refId": "B",
                "queryType": "",
                "relativeTimeRange": {
                    "from": 0,
                    "to": 0
                },
                "datasourceUid": "-100",
                "model": {
                    "type": "classic_conditions",
                    "refId": "B",
                    "datasource": {
                        "type": "__expr__",
                        "uid": "-100"
                    },
                    "conditions": [
                        {
                            "evaluator": {
                                "type": comparacao,
                                "params": [limite]
                            },
                            "operator": {"type": "and"},
                            "query": {"params": ["A"]},
                            "reducer": {
                                "type": "last",
                                "params": []
                            },
                            "type": "query"
                        }
                    ]
                }
            }
        ]
    }

    api("POST", "/api/v1/provisioning/alert-rules", regra)
    print(f"CRIADO: {titulo}")


# ALERTA 1 - CPU
criar_alerta(
    "mqiotcpu",
    "OAT2 - CPU elevada",
    'max(100 * rate(process_cpu_seconds_total{job="mecaniqa-iot"}[2m]) / 0.025)',
    "gt", 70, "1m"
)

# ALERTA 2 - MEMORIA
criar_alerta(
    "mqiotmem",
    "OAT2 - Memoria elevada",
    'max(100 * process_resident_memory_bytes{job="mecaniqa-iot"} / 33554432)',
    "gt", 80, "1m"
)

# ALERTA 3 - ERROS IOT
criar_alerta(
    "mqioterr",
    "OAT2 - Erros nas leituras IoT",
    'sum(rate(mecaniqa_leituras_erro_total{job="mecaniqa-iot"}[2m]))',
    "gt", 10, "1m"
)

# ALERTA 4 - QUEDA DE SUCESSOS
criar_alerta(
    "mqiotok",
    "OAT2 - Queda nas leituras de sucesso",
    'sum(rate(mecaniqa_leituras_sucesso_total{job="mecaniqa-iot"}[2m]))',
    "lt", 0.1, "2m"
)

# Conferir e registrar evidencias
regras = api("GET", "/api/v1/provisioning/alert-rules")

uids = {"mqiotcpu", "mqiotmem", "mqioterr", "mqiotok"}
nossas = [r for r in regras if r.get("uid") in uids]

destino = Path("evidencias/oat2/21-10/04-alertas-grafana.json")
destino.parent.mkdir(parents=True, exist_ok=True)

destino.write_text(
    json.dumps(nossas, indent=2, ensure_ascii=False)
)

print(f"\nREGRAS ENCONTRADAS: {len(nossas)}/4")
print(f"Evidencia salva em: {destino}")
