from dataclasses import dataclass
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


class FetchError(Exception):
    pass


@dataclass
class FetchResult:
    text: str
    method: str


def looks_like_xml(text: str) -> bool:
    head = text[:512]
    return ("<urlset" in head) or ("<sitemapindex" in head)


def _direct(url: str):
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    except Exception:
        return None
    if 200 <= resp.status_code < 300 and looks_like_xml(resp.text):
        return resp.text
    return None


def fetch(url: str, fallback=None, fallback_label: str = "fallback") -> FetchResult:
    """Fetch a sitemap. Tries a direct HTTP GET first; if that is blocked or
    fails, delegates to ``fallback(url) -> str`` (any unlocker/proxy the caller
    plugs in). The fetcher itself is vendor-neutral: concrete providers live in
    ``providers.py``. Raises FetchError if direct fails and no fallback is set."""
    text = _direct(url)
    if text is not None:
        return FetchResult(text=text, method="direct")
    if fallback is None:
        raise FetchError(f"Direct fetch failed/blocked for {url} and no fallback provider is configured")
    return FetchResult(text=fallback(url), method=fallback_label)
