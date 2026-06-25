from sitemap_compare.compare import Table
from sitemap_compare.render import table_to_html


def test_renders_headers_and_rows():
    t = Table(
        headers=["brightdata.com", "bright.cn"],
        matched_rows=[["https://brightdata.com/a", "https://www.bright.cn/a"]],
        orphan_rows=[["", "https://www.bright.cn/x"]],
    )
    html = table_to_html(t)
    assert "<table" in html and "</table>" in html
    assert "<th>brightdata.com</th>" in html
    assert 'href="https://brightdata.com/a"' in html
    assert html.count("<tr") == 3  # header + 1 matched + 1 orphan


def test_escapes_and_blank_cells():
    t = Table(headers=["a", "b"], matched_rows=[["https://x.com/?q=1&z=2", ""]], orphan_rows=[])
    html = table_to_html(t)
    assert "&amp;" in html       # ampersand escaped
    assert "<td></td>" in html   # blank cell empty


def test_cell_blocks_non_http_schemes():
    """javascript: and other non-http(s) values must not produce an <a> tag."""
    t = Table(
        headers=["URL"],
        matched_rows=[["javascript:alert(1)"]],
        orphan_rows=[],
    )
    html = table_to_html(t)
    # Must NOT contain an anchor tag
    assert "<a" not in html
    # Must contain the escaped text
    assert "javascript:alert(1)" in html


def test_cell_allows_https_url():
    """https:// URLs must still render as clickable links."""
    t = Table(
        headers=["URL"],
        matched_rows=[["https://example.com/page"]],
        orphan_rows=[],
    )
    html = table_to_html(t)
    assert 'href="https://example.com/page"' in html
    assert 'target="_blank"' in html      # opens a new tab, not the iframe


def test_has_light_theme_for_readability():
    """Output carries a white-background light theme so links aren't blue-on-black."""
    t = Table(headers=["a"], matched_rows=[["https://x.com/p"]], orphan_rows=[])
    html = table_to_html(t)
    assert "<style>" in html
    assert "#ffffff" in html        # white background
    assert 'class="smc"' in html    # scoped wrapper
