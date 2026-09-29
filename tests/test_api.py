from __future__ import annotations

from pathlib import Path

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
    for path in ["/", "/estimate", "/dashboard", "/model-card"]:
        response = client.get(path)
        assert response.status_code == 200
