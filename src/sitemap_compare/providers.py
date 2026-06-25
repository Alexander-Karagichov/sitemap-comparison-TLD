"""Swappable fetch-fallback providers.

The fetcher tries a direct request first and only needs a fallback for sitemaps
that block direct access. That fallback is pluggable: a provider is just a
callable ``(url: str) -> str`` that returns the sitemap XML or raises FetchError.

Built-in providers:
  - brightdata : Bright Data Web Unlocker REST API (the default)
  - proxy      : route the request through any HTTP(S) proxy / proxy-based
                 unlocker (Bright Data proxy mode, ScraperAPI, Oxylabs, your own)

To add your own, write a callable that returns XML and register it in PROVIDERS.
"""
import requests

from .fetcher import FetchError, looks_like_xml, UA

BRIGHTDATA_URL = "https://api.brightdata.com/request"


def brightdata_fallback(token: str, zone: str):
    """Bright Data Web Unlocker: POST the URL to the Bright Data API. Both the
    token and the zone name come from the caller's environment."""
    def _fetch(url: str) -> str:
        resp = requests.post(
            BRIGHTDATA_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"zone": zone, "url": url, "format": "raw"},
            timeout=60,
        )
        if 200 <= resp.status_code < 300 and looks_like_xml(resp.text):
            return resp.text
        raise FetchError(f"Bright Data fetch failed for {url} (status {resp.status_code})")

    return _fetch


def proxy_fallback(proxy_url: str):
    """Generic fallback: re-issue the request through an HTTP(S) proxy. Works
    with any proxy-based unlocker. ``proxy_url`` looks like
    http://user:pass@host:port ."""
    def _fetch(url: str) -> str:
        resp = requests.get(
            url,
            headers={"User-Agent": UA},
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=60,
        )
        if 200 <= resp.status_code < 300 and looks_like_xml(resp.text):
            return resp.text
        raise FetchError(f"Proxy fetch failed for {url} (status {resp.status_code})")

    return _fetch


# name -> factory(env) -> (callable | None). Add your own provider here.
PROVIDERS = {
    "brightdata": lambda env: (
        brightdata_fallback(env["BRIGHTDATA_API_TOKEN"], env["BRIGHTDATA_ZONE"])
        if env.get("BRIGHTDATA_API_TOKEN") and env.get("BRIGHTDATA_ZONE")
        else None
    ),
    "proxy": lambda env: (proxy_fallback(env["FETCH_PROXY_URL"]) if env.get("FETCH_PROXY_URL") else None),
}


def resolve_fallback(env):
    """Pick a fallback provider from environment config.

    Honors ``FETCH_PROVIDER`` (brightdata | proxy | none). If unset, auto-detects:
    Bright Data when a token is present, else proxy when a proxy URL is present,
    else no fallback. Returns ``(callable_or_None, label)``."""
    name = (env.get("FETCH_PROVIDER") or "").strip().lower()
    if not name:
        if env.get("BRIGHTDATA_API_TOKEN") and env.get("BRIGHTDATA_ZONE"):
            name = "brightdata"
        elif env.get("FETCH_PROXY_URL"):
            name = "proxy"
        else:
            name = "none"
    factory = PROVIDERS.get(name)
    fn = factory(env) if factory else None
    return (fn, name if fn else "none")
