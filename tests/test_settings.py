import os

from sitemap_compare.settings import load_settings, save_settings


def test_load_missing_returns_empty(tmp_path):
    assert load_settings(str(tmp_path / "nope.json")) == {}


def test_save_then_load_roundtrip(tmp_path):
    path = str(tmp_path / "settings.json")
    data = {
        "main_url": "https://brightdata.com/sitemap_index.xml",
        "tld_urls": ["https://brightdata.es/sitemap_index.xml"],
        "aliases": [{"treat": "/blog/datos-web", "as": "/blog/web-data"}],
    }
    save_settings(path, data)
    assert load_settings(path) == data


def test_load_corrupt_returns_empty(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("{not valid json", encoding="utf-8")
    assert load_settings(str(path)) == {}


def test_save_preserves_non_ascii(tmp_path):
    path = str(tmp_path / "s.json")
    save_settings(path, {"aliases": [{"treat": "/categoría", "as": "/category"}]})
    assert load_settings(path)["aliases"][0]["treat"] == "/categoría"
