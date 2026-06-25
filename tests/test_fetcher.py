import pytest
import sitemap_compare.fetcher as f
from sitemap_compare.fetcher import fetch, looks_like_xml, FetchError


class FakeResp:
    def __init__(self, status, text):
        self.status_code = status
        self.text = text


def test_looks_like_xml():
    assert looks_like_xml("<urlset xmlns=...>")
    assert looks_like_xml("<sitemapindex>")
    assert not looks_like_xml("<html><body>blocked</body></html>")


def test_direct_success(monkeypatch):
    monkeypatch.setattr(f.requests, "get", lambda *a, **k: FakeResp(200, "<urlset></urlset>"))
    r = fetch("https://x.com/sm.xml")
    assert r.method == "direct"
    assert "urlset" in r.text


def test_uses_fallback_when_direct_blocked(monkeypatch):
    monkeypatch.setattr(f.requests, "get", lambda *a, **k: FakeResp(403, "<html>blocked</html>"))
    r = fetch("https://x.com/sm.xml", fallback=lambda u: "<urlset></urlset>", fallback_label="brightdata")
    assert r.method == "brightdata"
    assert "urlset" in r.text


def test_no_fallback_and_blocked_raises(monkeypatch):
    monkeypatch.setattr(f.requests, "get", lambda *a, **k: FakeResp(403, "<html>blocked</html>"))
    with pytest.raises(FetchError):
        fetch("https://x.com/sm.xml", fallback=None)
