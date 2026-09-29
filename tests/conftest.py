from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_payload():
    schema = json.loads(
        (ROOT / "reports" / "results" / "input_schema.json").read_text(encoding="utf-8")
    )
    return {feature: bounds["median"] for feature, bounds in schema.items()}
