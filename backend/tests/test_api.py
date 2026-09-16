from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_metadados():
    assert len(client.get("/api/v1/eixos").json()["eixos"]) == 5
    veic = client.get("/api/v1/veiculos").json()["veiculos"]
    assert len(veic) == 3
    assert {v["nome"]: v["selecionavel"] for v in veic}["MOTOS"] is False


def test_otimizar_gate():
    r = client.post("/api/v1/otimizar", json={"eixo": 4, "veiculo": "ACELLO 815"})
    assert r.status_code == 200
    t = r.json()["totais"]
    assert t["quantidade_pedidos"] == 7
    assert abs(t["peso_utilizado"] - 4797.335) < 0.01
    assert r.json()["gargalo"] == "PESO"


def test_otimizar_motos_400():
    r = client.post("/api/v1/otimizar", json={"eixo": 4, "veiculo": "MOTOS"})
    assert r.status_code == 400


def test_insight_sem_chave_503():
    plano = client.post("/api/v1/otimizar", json={"eixo": 4, "veiculo": "ACELLO 815"}).json()
    r = client.post("/api/v1/insight", json={"plano": plano})
    assert r.status_code == 503  # fallback silencioso (sem ANTHROPIC_API_KEY)


def test_ingest_substitui_semana():
    with open("data/pedidos_semana_4.csv", "rb") as f:
        r = client.post("/api/v1/etl/ingest",
                        files={"semana_4": ("s4.csv", f, "text/csv")})
    assert r.status_code == 200
    assert r.json()["semanas_atualizadas"] == [4]
    assert r.json()["resumo_qualidade"]["registros_processados"] == 688


def test_ingest_colunas_invalidas_400():
    r = client.post("/api/v1/etl/ingest",
                    files={"semana_1": ("x.csv", b"col_errada;outra\n1;2\n", "text/csv")})
    assert r.status_code == 400


def test_revisar_cubagem_uc07():
    ped = client.get("/api/v1/pedidos?eixo=1").json()["pedidos"][0]
    cod = ped["itens"][0]["codigo"]
    r = client.post(f"/api/v1/pedidos/{ped['pedido']}/revisar",
                    json={"itens": [{"codigo": cod, "peso_kg": 10.0, "volume_m3": 0.05}]})
    assert r.status_code == 200
    assert r.json()["qualidade_cubagem"] == "ESTIMADA"
