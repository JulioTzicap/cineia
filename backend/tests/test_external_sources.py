from app import main


class FakeResponse:
    def __init__(self, payload=None, content=b"", status_code=200):
        self._payload = payload or {}
        self.content = content
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise main.httpx.HTTPStatusError("error", request=None, response=None)


def test_google_news_extracts_sources(monkeypatch):
    xml = b"""<rss><channel><item><title>Noticia CineIA</title><link>https://example.test/noticia</link><pubDate>Fri, 06 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>"""
    monkeypatch.setattr(main.httpx, "get", lambda *args, **kwargs: FakeResponse(content=xml))
    rows = main.google_news("Dune")
    assert rows == [{
        "title": "Noticia CineIA",
        "url": "https://example.test/noticia",
        "date": "Fri, 06 Nov 2026 10:00:00 GMT",
    }]


def test_wikipedia_extracts_summary_and_url(monkeypatch):
    payload = {"query": {"pages": {"1": {"title": "Interstellar", "extract": "Resumen verificable", "fullurl": "https://es.wikipedia.org/wiki/Interstellar"}}}}
    monkeypatch.setattr(main.httpx, "get", lambda *args, **kwargs: FakeResponse(payload=payload))
    result = main.wikipedia_details("Interestelar")
    assert result["title"] == "Interstellar"
    assert result["extract"] == "Resumen verificable"
    assert result["url"].startswith("https://")


def test_bi_rejects_invalid_key_before_querying_database():
    try:
        main.bi("clave-incorrecta")
        assert False, "La API BI debe rechazar una clave inválida"
    except main.HTTPException as exc:
        assert exc.status_code == 401
