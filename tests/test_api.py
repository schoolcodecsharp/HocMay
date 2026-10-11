from __future__ import annotations

from pathlib import Path
import pytest

from app.model_service import model_service


def test_valid_request(client, valid_payload):
    response = client.post("/api/estimate", json=valid_payload)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["prediction"], float)
    assert body["estimated_usd"] == body["prediction"] * 100_000
    assert "census block group" in body["warning"]


def test_missing_field(client, valid_payload):
    valid_payload.pop("MedInc")
    response = client.post("/api/estimate", json=valid_payload)
    assert response.status_code == 422


def test_wrong_data_type(client, valid_payload):
    valid_payload["HouseAge"] = "không phải số"
    response = client.post("/api/estimate", json=valid_payload)
    assert response.status_code == 422


def test_outside_domain(client, valid_payload):
    valid_payload["Latitude"] = 999
    response = client.post("/api/estimate", json=valid_payload)
    assert response.status_code == 422


def test_nan_is_rejected(client, valid_payload):
    valid_payload["MedInc"] = "NaN"
    response = client.post("/api/estimate", json=valid_payload)
    assert response.status_code == 422


def test_missing_model_returns_503(client, valid_payload, tmp_path: Path):
    old_path = model_service.model_path
    old_pipeline = model_service.pipeline
    try:
        model_service.model_path = tmp_path / "missing.joblib"
        model_service.pipeline = None
        response = client.post("/api/estimate", json=valid_payload)
        assert response.status_code == 503
    finally:
        model_service.model_path = old_path
        model_service.pipeline = old_pipeline


def test_pages_are_available(client):
    for path in ["/", "/estimate", "/dashboard", "/model-card", "/data"]:
        response = client.get(path)
        assert response.status_code == 200


@pytest.mark.parametrize("value", [True, "3.54", None, {}, [], False])
def test_strict_json_numbers(client, valid_payload, value):
    valid_payload["MedInc"] = value
    assert client.post("/api/estimate", json=valid_payload).status_code == 422


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_raw_json_is_safe(client, valid_payload, literal):
    import json

    content = json.dumps(valid_payload).replace(
        str(valid_payload["MedInc"]), literal, 1
    )
    response = client.post(
        "/api/estimate", content=content, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json()["detail"]


def test_cross_field_validation(client, valid_payload):
    valid_payload.update(AveRooms=1, AveBedrms=2)
    assert client.post("/api/estimate", json=valid_payload).status_code == 422


def test_extra_field(client, valid_payload):
    valid_payload["target"] = 1
    assert client.post("/api/estimate", json=valid_payload).status_code == 422


def test_malformed_json(client):
    assert (
        client.post(
            "/api/estimate", content="{", headers={"Content-Type": "application/json"}
        ).status_code
        == 422
    )


def test_corrupt_model(client, valid_payload, tmp_path, monkeypatch):
    bad = tmp_path / "bad.joblib"
    bad.write_bytes(b"not a model")
    monkeypatch.setattr(model_service, "model_path", bad)
    monkeypatch.setattr(model_service, "pipeline", None)
    assert client.post("/api/estimate", json=valid_payload).status_code == 503


def test_missing_schema(client, valid_payload, tmp_path, monkeypatch):
    import app.model_service as service_module

    monkeypatch.setattr(service_module, "SCHEMA_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(model_service, "pipeline", None)
    assert client.post("/api/estimate", json=valid_payload).status_code == 503


def test_prediction_does_not_fit(client, valid_payload, monkeypatch):
    model_service.ensure_loaded()

    def forbidden(*args, **kwargs):
        raise AssertionError("Serving must never fit")

    monkeypatch.setattr(model_service.pipeline, "fit", forbidden)
    monkeypatch.setattr(model_service.pipeline.named_steps["scaler"], "fit", forbidden)
    assert client.post("/api/estimate", json=valid_payload).status_code == 200


def test_data_pagination(client):
    response = client.get("/api/data?offset=0&limit=3")
    if response.status_code == 503:
        pytest.skip("Database not imported locally")
    data = response.json()
    assert len(data["rows"]) == 3 and data["total"] == 14448
    assert all(row["split"] == "train" for row in data["rows"])
    assert client.get("/api/data?limit=1000").status_code == 422
    assert client.get("/api/data?offset=-1").status_code == 422


@pytest.mark.parametrize(
    "bounds",
    [
        {"min": "bad", "median": 3, "max": 5},
        {"min": 5, "median": 3, "max": 1},
        {"median": 3, "max": 5},
    ],
)
def test_corrupt_schema_bounds_returns_503(
    client, valid_payload, tmp_path, monkeypatch, bounds
):
    import json
    import app.model_service as service_module

    schema = json.loads(service_module.SCHEMA_PATH.read_text(encoding="utf-8"))
    schema["MedInc"] = bounds
    bad = tmp_path / "schema.json"
    bad.write_text(json.dumps(schema), encoding="utf-8")
    monkeypatch.setattr(service_module, "SCHEMA_PATH", bad)
    monkeypatch.setattr(model_service, "pipeline", None)
    assert client.post("/api/estimate", json=valid_payload).status_code == 503


def test_fractional_population_rejected(client, valid_payload):
    valid_payload["Population"] = 1168.5
    assert client.post("/api/estimate", json=valid_payload).status_code == 422


def test_prediction_failure_returns_500(client, valid_payload, monkeypatch):
    def fail(*args):
        raise ArithmeticError("Internal error")

    monkeypatch.setattr(model_service, "predict", fail)
    response = client.post("/api/estimate", json=valid_payload)
    assert response.status_code == 500
    assert "Internal error" not in response.text


def test_missing_database_returns_503(client, tmp_path, monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "DB_PATH", tmp_path / "missing.sqlite3")
    assert client.get("/api/data").status_code == 503
    assert not (tmp_path / "missing.sqlite3").exists()


@pytest.mark.parametrize("value", [10**400, -(10**400)])
def test_huge_json_integer_rejected(client, valid_payload, value):
    valid_payload["MedInc"] = value
    assert client.post("/api/estimate", json=valid_payload).status_code == 422


def test_huge_pagination_offset_rejected(client):
    assert client.get(f"/api/data?offset={10**400}").status_code == 422


def test_page_after_last_is_empty(client):
    response = client.get("/api/data?offset=20640")
    if response.status_code == 503:
        pytest.skip("Database not imported locally")
    assert response.status_code == 200
    assert response.json()["rows"] == []
