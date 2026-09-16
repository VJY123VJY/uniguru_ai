from fastapi.testclient import TestClient

from service.api import app


TEST_TOKEN = "phase2-test-token"
ALLOWED_CALLER = "internal-testing"
QUERY = "What is counting?"

ALLOWED_CALLERS = {
    "bhiv-assistant",
    "gurukul-platform",
    "internal-testing",
    "uniguru-frontend",
}


def _client(monkeypatch):
    monkeypatch.setenv("UNIGURU_API_AUTH_REQUIRED", "true")
    monkeypatch.setenv("UNIGURU_API_TOKENS", TEST_TOKEN)
    monkeypatch.setenv(
        "UNIGURU_ALLOWED_CALLERS",
        "bhiv-assistant,gurukul-platform,internal-testing,uniguru-frontend",
    )

    import service.api as api

    monkeypatch.setattr(api, "_is_pytest_runtime", lambda: False)
    monkeypatch.setattr(api, "_API_AUTH_REQUIRED", True)
    monkeypatch.setattr(api, "_AUTH_MODE", "strict")
    monkeypatch.setattr(api, "_API_TOKENS", {TEST_TOKEN})
    monkeypatch.setattr(api, "_ALLOWED_CALLERS", ALLOWED_CALLERS)

    return TestClient(app)


def _payload():
    return {
        "query": QUERY,
        "context": {
            "caller": ALLOWED_CALLER,
        },
    }


def test_ask_requires_service_token(monkeypatch):
    client = _client(monkeypatch)

    response = client.post("/ask", json=_payload())

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_ask_rejects_invalid_service_token(monkeypatch):
    client = _client(monkeypatch)

    response = client.post(
        "/ask",
        json=_payload(),
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_ask_rejects_unauthorized_caller(monkeypatch):
    client = _client(monkeypatch)

    payload = {
        "query": QUERY,
        "context": {
            "caller": "unauthorized-client",
        },
    }

    response = client.post(
        "/ask",
        json=payload,
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()


def test_ask_accepts_valid_token_and_allowed_caller(monkeypatch):
    client = _client(monkeypatch)

    response = client.post(
        "/ask",
        json=_payload(),
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["decision"] == "answer"
    assert body["verification_status"] == "VERIFIED"
    assert body["answer"]
    assert body["curriculum_capability"]["capability"]["id"] == (
        "tantra.curriculum_intelligence"
    )


def test_ask_validation_error_remains_422(monkeypatch):
    client = _client(monkeypatch)

    response = client.post("/ask", json={})

    assert response.status_code == 422


def test_ask_unknown_canonical_knowledge_is_blocked(monkeypatch):
    client = _client(monkeypatch)

    payload = {
        "query": "Explain the fictional Balbharti quantum teleportation method",
        "context": {
            "caller": ALLOWED_CALLER,
        },
    }

    response = client.post(
        "/ask",
        json=payload,
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"] == "block"
    assert body["answer"] is None
    assert body["verification_status"] == "BLOCKED"
    assert body["status_action"] == "BLOCK"
    assert "no canonical retrieval match" in body["reason"].lower()


def test_health_is_public(monkeypatch):
    client = _client(monkeypatch)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "ok"
    assert body["service"] == "uniguru-live-reasoning"


def test_ready_is_public(monkeypatch):
    client = _client(monkeypatch)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] in {"ready", "degraded"}


def test_health_live_is_public(monkeypatch):
    client = _client(monkeypatch)

    response = client.get("/health/live")

    assert response.status_code == 200


def test_metrics_requires_auth(monkeypatch):
    client = _client(monkeypatch)

    response = client.get("/metrics")

    assert response.status_code == 401


def test_metrics_accepts_valid_auth(monkeypatch):
    client = _client(monkeypatch)

    response = client.get(
        "/metrics",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "uniguru_requests_total" in response.text


def test_ask_exposes_observability_headers(monkeypatch):
    client = _client(monkeypatch)

    response = client.post(
        "/ask",
        json=_payload(),
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )

    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Window-Seconds" in response.headers
    assert "X-Request-Latency-Ms" in response.headers

    float(response.headers["X-Request-Latency-Ms"])
    int(response.headers["X-RateLimit-Limit"])
    int(response.headers["X-RateLimit-Window-Seconds"])


def test_ask_replay_preserves_canonical_evidence(monkeypatch):
    client = _client(monkeypatch)
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

    first = client.post("/ask", json=_payload(), headers=headers)
    second = client.post("/ask", json=_payload(), headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200

    first_body = first.json()
    second_body = second.json()

    assert first_body["decision"] == "answer"
    assert second_body["decision"] == "answer"
    assert first_body["verification_status"] == "VERIFIED"
    assert second_body["verification_status"] == "VERIFIED"

    first_result = first_body["curriculum_capability"]["result"]
    second_result = second_body["curriculum_capability"]["result"]

    # Request IDs/timestamps are expected to differ between executions.
    assert first_result["request_id"] != second_result["request_id"]
    assert first_result["timestamp"] != second_result["timestamp"]

    # Canonical evidence identity and provenance must remain stable.
    stable_fields = (
        "evidence_id",
        "textbook_id",
        "edition",
        "chapter",
        "section",
        "page_numbers",
        "source_hash",
        "retrieval_hash",
        "lineage_hash",
        "verification_status",
    )

    for field in stable_fields:
        assert first_result.get(field) == second_result.get(field), field

    assert first_body["curriculum_capability"]["result"]["runtime_evidence"] == (
        second_body["curriculum_capability"]["result"]["runtime_evidence"]
    )
