from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from app import main


def test_admin_allows_admin_role():
    user = {"id": "demo", "role": "ADMIN"}
    assert main.admin(user) == user


def test_admin_rejects_regular_user():
    try:
        main.admin({"id": "demo", "role": "USER"})
        assert False, "Un usuario regular no debe acceder a administración"
    except HTTPException as exc:
        assert exc.status_code == 403


def test_generated_token_contains_identity_and_role():
    token = main.token_for({"id": "user-123", "role": "USER"})
    data = jwt.decode(token, main.JWT_SECRET, algorithms=["HS256"])
    assert data["sub"] == "user-123"
    assert data["role"] == "USER"


def test_password_hash_is_not_plain_text():
    password = "CineIA_Prueba_2026!"
    password_hash = main.pwd.hash(password)
    assert password_hash != password
    assert main.pwd.verify(password, password_hash)


def test_admin_cannot_deactivate_itself():
    body = main.UserUpdate(
        full_name="Administrador",
        role="ADMIN",
        is_active=False,
        token_limit_monthly=20000,
    )
    try:
        main.update_user("admin-id", body, {"id": "admin-id", "role": "ADMIN"})
        assert False, "El administrador no debe poder desactivarse a sí mismo"
    except HTTPException as exc:
        assert exc.status_code == 400


def test_admin_cannot_remove_own_role():
    body = main.UserUpdate(
        full_name="Administrador",
        role="USER",
        is_active=True,
        token_limit_monthly=20000,
    )
    try:
        main.update_user("admin-id", body, {"id": "admin-id", "role": "ADMIN"})
        assert False, "El administrador no debe quitarse su propio rol"
    except HTTPException as exc:
        assert exc.status_code == 400


def test_groq_chat_returns_real_usage_shape(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [{"message": {"content": "Respuesta de prueba"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 5},
            }

    monkeypatch.setattr(main, "GROQ_API_KEY", "gsk_test")
    monkeypatch.setattr(main.httpx, "post", lambda *args, **kwargs: FakeResponse())
    answer, incoming, outgoing = main.groq_chat([{"role": "user", "content": "Hola"}])
    assert answer == "Respuesta de prueba"
    assert incoming == 12
    assert outgoing == 5


def test_regular_user_receives_403_on_admin_route():
    main.app.dependency_overrides[main.current] = lambda: {"id": "user-id", "role": "USER"}
    try:
        response = TestClient(main.app).get("/api/v1/admin/users")
        assert response.status_code == 403
    finally:
        main.app.dependency_overrides.clear()


def test_disabled_service_is_blocked(monkeypatch):
    class Result:
        def first(self):
            return None

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, *args, **kwargs):
            return Result()

    monkeypatch.setattr(main, "db", lambda: Connection())
    try:
        main.enabled("rag")
        assert False, "Un servicio desactivado debe quedar bloqueado"
    except HTTPException as exc:
        assert exc.status_code == 503
