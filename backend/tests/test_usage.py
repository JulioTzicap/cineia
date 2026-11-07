from fastapi import HTTPException

from app import main


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class FakeConnection:
    def __init__(self, values):
        self.values = iter(values)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, *args, **kwargs):
        return ScalarResult(next(self.values))


def test_quota_returns_remaining_balance(monkeypatch):
    monkeypatch.setattr(main, "db", lambda: FakeConnection([250, 2000]))
    result = main.ensure_quota({"id": "user"}, estimated_tokens=500)
    assert result == {"used": 250, "limit": 2000, "remaining": 1750}


def test_quota_blocks_before_calling_ai(monkeypatch):
    monkeypatch.setattr(main, "db", lambda: FakeConnection([1900, 2000]))
    try:
        main.ensure_quota({"id": "user"}, estimated_tokens=500)
        assert False, "La cuota insuficiente debe bloquear la solicitud"
    except HTTPException as exc:
        assert exc.status_code == 429
        assert "insuficiente" in exc.detail


def test_inactive_user_is_rejected_by_quota(monkeypatch):
    monkeypatch.setattr(main, "db", lambda: FakeConnection([0, None]))
    try:
        main.ensure_quota({"id": "user"}, estimated_tokens=100)
        assert False, "El usuario inactivo debe ser rechazado"
    except HTTPException as exc:
        assert exc.status_code == 403
