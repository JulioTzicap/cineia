from app import main


def test_catalog_context_uses_semantic_fallback_when_exact_search_is_empty(monkeypatch):
    expected = ("- Interestelar (MOVIE)", [{"id": "1", "title": "Interestelar", "type": "catalog"}])
    monkeypatch.setattr(main, "rag_reply", lambda _message: ("", []))
    monkeypatch.setattr(main, "preference_candidates", lambda _message: expected)

    assert main.catalog_context("¿Qué películas de ciencia ficción hay disponibles?") == expected


def test_catalog_context_preserves_exact_catalog_matches(monkeypatch):
    expected = ("- Interestelar (MOVIE)", [{"id": "1", "title": "Interestelar", "type": "catalog"}])
    monkeypatch.setattr(main, "rag_reply", lambda _message: expected)
    monkeypatch.setattr(main, "preference_candidates", lambda _message: (_ for _ in ()).throw(AssertionError("No debe usarse el respaldo")))

    assert main.catalog_context("¿De qué trata Interestelar?") == expected
