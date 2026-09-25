from __future__ import annotations

import inspect
from typing import get_type_hints

import pytest
from pydantic import ValidationError

from service import api


def test_chat_create_request_is_strict():
    valid = api.ChatCreateRequest(guruId="guru-1")
    assert valid.guruId == "guru-1"

    with pytest.raises(ValidationError):
        api.ChatCreateRequest()

    with pytest.raises(ValidationError):
        api.ChatCreateRequest(guruId="guru-1", unexpected="x")


def test_chat_update_request_is_strict_but_allows_empty_patch():
    assert api.ChatUpdateRequest().model_dump(exclude_unset=True) == {}

    valid = api.ChatUpdateRequest(
        title="Updated",
        isArchived=True,
        isActive=False,
    )
    assert valid.title == "Updated"
    assert valid.isArchived is True
    assert valid.isActive is False

    with pytest.raises(ValidationError):
        api.ChatUpdateRequest(extra_field="x")


def test_chat_message_request_is_strict():
    valid = api.ChatMessageRequest(
        message="Hello",
        chatbotId="guru-1",
    )
    assert valid.message == "Hello"

    with pytest.raises(ValidationError):
        api.ChatMessageRequest(message="Hello")

    with pytest.raises(ValidationError):
        api.ChatMessageRequest(chatbotId="guru-1")

    with pytest.raises(ValidationError):
        api.ChatMessageRequest(
            message="Hello",
            chatbotId="guru-1",
            unexpected="x",
        )


def test_google_oauth_request_is_strict():
    valid = api.GoogleOAuthTokenRequest(token="token-value")
    assert valid.token == "token-value"

    with pytest.raises(ValidationError):
        api.GoogleOAuthTokenRequest()

    with pytest.raises(ValidationError):
        api.GoogleOAuthTokenRequest(token="token-value", extra="x")


def test_login_request_is_strict():
    valid = api.UserLoginRequest(
        email="user@example.com",
        password="secret",
    )
    assert valid.email == "user@example.com"

    with pytest.raises(ValidationError):
        api.UserLoginRequest(email="user@example.com")

    with pytest.raises(ValidationError):
        api.UserLoginRequest(password="secret")

    with pytest.raises(ValidationError):
        api.UserLoginRequest(
            email="user@example.com",
            password="secret",
            extra="x",
        )


def test_signup_request_is_strict():
    valid = api.UserSignupRequest(
        name="Test User",
        email="user@example.com",
        password="secret",
    )
    assert valid.name == "Test User"

    with pytest.raises(ValidationError):
        api.UserSignupRequest(
            email="user@example.com",
            password="secret",
        )

    with pytest.raises(ValidationError):
        api.UserSignupRequest(
            name="Test User",
            password="secret",
        )

    with pytest.raises(ValidationError):
        api.UserSignupRequest(
            name="Test User",
            email="user@example.com",
        )

    with pytest.raises(ValidationError):
        api.UserSignupRequest(
            name="Test User",
            email="user@example.com",
            password="secret",
            extra="x",
        )


def test_strict_request_models_forbid_extra_fields():
    model_classes = (
        api.ChatCreateRequest,
        api.ChatUpdateRequest,
        api.ChatMessageRequest,
        api.GoogleOAuthTokenRequest,
        api.UserLoginRequest,
        api.UserSignupRequest,
    )

    for model in model_classes:
        assert model.model_config.get("extra") == "forbid"


def test_chat_handlers_use_pydantic_request_models():
    expected = {
        "chat_create": api.ChatCreateRequest,
        "chat_update": api.ChatUpdateRequest,
        "chat_new": api.ChatMessageRequest,
        "google_oauth_callback": api.GoogleOAuthTokenRequest,
        "user_login": api.UserLoginRequest,
        "user_signup": api.UserSignupRequest,
    }

    for function_name, expected_model in expected.items():
        function = getattr(api, function_name)
        signature = inspect.signature(function)
        type_hints = get_type_hints(function)
        body_parameters = [
            parameter
            for parameter in signature.parameters.values()
            if parameter.name == "request_body"
        ]
        assert len(body_parameters) == 1
        assert type_hints["request_body"] is expected_model

@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("post", "/chat/create", {"unexpected": "x"}),
        ("put", "/chat/chat/test-chat", {"unexpected": "x"}),
        (
            "post",
            "/chat/new",
            {"message": "hello", "chatbotId": "guru-1", "unexpected": "x"},
        ),
        ("post", "/auth/google/token", {"unexpected": "x"}),
        (
            "post",
            "/user/login",
            {"email": "user@example.com", "password": "secret", "unexpected": "x"},
        ),
        (
            "post",
            "/user/signup",
            {
                "name": "Test User",
                "email": "user@example.com",
                "password": "secret",
                "unexpected": "x",
            },
        ),
    ],
)
def test_http_boundary_rejects_unknown_request_fields(method, path, payload):
    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    response = getattr(client, method)(path, json=payload)

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body

def test_new_rag_rejects_unknown_fields():
    from fastapi.testclient import TestClient
    from service.api import app

    client = TestClient(app)
    response = client.post(
        "/new_rag",
        json={"query": "What is counting?", "unexpected_field": "X"},
        headers={"Authorization": "Bearer uniguru_secret_123"},
    )

    assert response.status_code == 422
    assert any(
        error.get("type") == "extra_forbidden"
        for error in response.json().get("detail", [])
    )


def test_new_query_rejects_unknown_fields():
    from fastapi.testclient import TestClient
    from service.api import app

    client = TestClient(app)
    response = client.post(
        "/new_query",
        json={"query": "What is counting?", "unexpected_field": "X"},
        headers={"Authorization": "Bearer uniguru_secret_123"},
    )

    assert response.status_code == 422
    assert any(
        error.get("type") == "extra_forbidden"
        for error in response.json().get("detail", [])
    )


def test_new_rag_preserves_http_401():
    from fastapi.testclient import TestClient
    from service.api import app

    client = TestClient(app)
    response = client.post(
        "/new_rag",
        json={"query": "What is counting?"},
        headers={"Authorization": "Bearer definitely-wrong-token"},
    )

    assert response.status_code == 401


def test_new_query_preserves_http_401():
    from fastapi.testclient import TestClient
    from service.api import app

    client = TestClient(app)
    response = client.post(
        "/new_query",
        json={"query": "What is counting?"},
        headers={"Authorization": "Bearer definitely-wrong-token"},
    )

    assert response.status_code == 401


def test_create_guru_request_is_strict():
    from service.guru_models import CreateGuruRequest

    valid = CreateGuruRequest(
        name="Math Guru",
        subject="Mathematics",
        description="Test guru",
    )
    assert valid.name == "Math Guru"

    with pytest.raises(ValidationError):
        CreateGuruRequest(
            name="Math Guru",
            subject="Mathematics",
            unexpected="x",
        )

    assert CreateGuruRequest.model_config.get("extra") == "forbid"

def test_openapi_resolves_all_structured_request_models():
    schema = api.app.openapi()

    expected = {
        "/ask": ("post", "AskRequest"),
        "/guru/custom-guru/{user_id}": ("post", "CreateGuruRequest"),
        "/guru/custom-guru/": ("post", "CreateGuruRequest"),
        "/chat/create": ("post", "ChatCreateRequest"),
        "/chat/chat/{chat_id}": ("put", "ChatUpdateRequest"),
        "/chat/new": ("post", "ChatMessageRequest"),
        "/auth/google/token": ("post", "GoogleOAuthTokenRequest"),
        "/user/login": ("post", "UserLoginRequest"),
        "/user/signup": ("post", "UserSignupRequest"),
        "/new_rag": ("post", "NewRagRequest"),
        "/new_query": ("post", "CoreRequest"),
    }

    component_schemas = schema["components"]["schemas"]

    for path, (method, model_name) in expected.items():
        operation = schema["paths"][path][method]
        request_body = operation["requestBody"]
        assert "application/json" in request_body["content"]

        schema_text = str(request_body["content"]["application/json"]["schema"])
        assert model_name in schema_text
        assert model_name in component_schemas

def test_all_structured_routes_reject_unknown_fields():
    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    headers = {"Authorization": "Bearer uniguru_secret_123"}

    cases = [
        ("POST", "/ask", {"__unexpected__": "x"}),
        ("POST", "/guru/custom-guru/test-user", {"__unexpected__": "x"}),
        ("POST", "/guru/custom-guru/", {"__unexpected__": "x"}),
        ("POST", "/chat/create", {"__unexpected__": "x"}),
        ("PUT", "/chat/chat/test-chat", {"__unexpected__": "x"}),
        ("POST", "/chat/new", {"__unexpected__": "x"}),
        ("POST", "/auth/google/token", {"__unexpected__": "x"}),
        ("POST", "/user/login", {"__unexpected__": "x"}),
        ("POST", "/user/signup", {"__unexpected__": "x"}),
        ("POST", "/new_rag", {"__unexpected__": "x"}),
        ("POST", "/new_query", {"__unexpected__": "x"}),
    ]

    for method, path, payload in cases:
        response = client.request(
            method,
            path,
            json=payload,
            headers=headers,
        )
        assert response.status_code == 422, (
            f"{method} {path} returned {response.status_code}: "
            f"{response.text[:500]}"
        )
