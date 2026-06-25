import pytest

import sitemap_compare.providers as p
from sitemap_compare.providers import (
    brightdata_fallback,
    proxy_fallback,
    resolve_fallback,
)
from sitemap_compare.fetcher import FetchError


class FakeResp:
    def __init__(self, status, text):
        self.status_code = status
        self.text = text


def test_brightdata_fallback_posts_and_returns_xml(monkeypatch):
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs.get("json")
        captured["headers"] = kwargs.get("headers")
        return FakeResp(200, "<urlset></urlset>")

    monkeypatch.setattr(p.requests, "post", fake_post)
    fn = brightdata_fallback("tok", "my_zone")
    assert "urlset" in fn("https://x.com/sm.xml")
    assert captured["url"] == p.BRIGHTDATA_URL
    assert captured["json"] == {"zone": "my_zone", "url": "https://x.com/sm.xml", "format": "raw"}
    assert captured["headers"]["Authorization"] == "Bearer tok"


def test_brightdata_fallback_raises_on_failure(monkeypatch):
    monkeypatch.setattr(p.requests, "post", lambda *a, **k: FakeResp(403, "<html>no</html>"))
    with pytest.raises(FetchError):
        brightdata_fallback("tok", "my_zone")("https://x.com/sm.xml")


def test_proxy_fallback_routes_through_proxy(monkeypatch):
    captured = {}

    def fake_get(url, **kwargs):
        captured["proxies"] = kwargs.get("proxies")
        return FakeResp(200, "<urlset></urlset>")

    monkeypatch.setattr(p.requests, "get", fake_get)
    fn = proxy_fallback("http://user:pass@host:222")
    assert "urlset" in fn("https://x.com/sm.xml")
    assert captured["proxies"] == {"http": "http://user:pass@host:222", "https": "http://user:pass@host:222"}


def test_resolve_defaults_to_brightdata_when_token_and_zone_present():
    fn, label = resolve_fallback({"BRIGHTDATA_API_TOKEN": "tok", "BRIGHTDATA_ZONE": "my_zone"})
    assert label == "brightdata" and fn is not None


def test_resolve_uses_proxy_when_only_proxy_set():
    fn, label = resolve_fallback({"FETCH_PROXY_URL": "http://h:1"})
    assert label == "proxy" and fn is not None


def test_resolve_explicit_provider_overrides_autodetect():
    # Token + zone present but FETCH_PROVIDER forces proxy; no proxy URL -> no fallback.
    fn, label = resolve_fallback(
        {"BRIGHTDATA_API_TOKEN": "tok", "BRIGHTDATA_ZONE": "my_zone", "FETCH_PROVIDER": "proxy"}
    )
    assert fn is None and label == "none"


def test_resolve_none_when_nothing_configured():
    fn, label = resolve_fallback({})
    assert fn is None and label == "none"
