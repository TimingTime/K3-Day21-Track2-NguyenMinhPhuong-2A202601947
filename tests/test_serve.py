from fastapi.testclient import TestClient

import src.serve as serve


class DummyModel:
    def predict(self, features):
        assert features.shape == (1, serve.EXPECTED_FEATURE_COUNT)
        return [2]


def test_health_endpoint():
    client = TestClient(serve.app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint(monkeypatch):
    monkeypatch.setattr(serve, "model", DummyModel())
    client = TestClient(serve.app)
    response = client.post(
        "/predict",
        json={"features": [0.0] * serve.EXPECTED_FEATURE_COUNT},
    )

    assert response.status_code == 200
    assert response.json() == {"prediction": 2, "label": "cao"}


def test_predict_rejects_wrong_feature_count(monkeypatch):
    monkeypatch.setattr(serve, "model", DummyModel())
    client = TestClient(serve.app)
    response = client.post("/predict", json={"features": [0.0, 1.0]})

    assert response.status_code == 400
