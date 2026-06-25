from sitemap_compare.sitemap import parse, collect

URLSET = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://x.com/a</loc></url>
  <url><loc> https://x.com/b </loc></url>
</urlset>"""

INDEX = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://x.com/sm1.xml</loc></sitemap>
  <sitemap><loc>https://x.com/sm2.xml</loc></sitemap>
</sitemapindex>"""

CHILD1 = """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://x.com/a</loc></url></urlset>"""
CHILD2 = """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://x.com/b</loc></url></urlset>"""


IMAGE_URLSET = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://x.com/page</loc>
    <image:image><image:loc>https://x.com/logo.svg</image:loc></image:image>
    <image:image><image:loc>https://x.com/hero.png</image:loc></image:image>
  </url>
</urlset>"""


def test_parse_urlset():
    kind, urls = parse(URLSET)
    assert kind == "urlset"
    assert urls == ["https://x.com/a", "https://x.com/b"]


def test_parse_ignores_image_loc():
    # Image-extension <image:loc> entries (e.g. .svg/.png assets) must NOT be
    # treated as page URLs; only the page's direct <loc> child counts.
    kind, urls = parse(IMAGE_URLSET)
    assert kind == "urlset"
    assert urls == ["https://x.com/page"]


def test_parse_index():
    kind, urls = parse(INDEX)
    assert kind == "index"
    assert urls == ["https://x.com/sm1.xml", "https://x.com/sm2.xml"]


def test_collect_recurses_index():
    pages = {
        "https://x.com/index.xml": INDEX,
        "https://x.com/sm1.xml": CHILD1,
        "https://x.com/sm2.xml": CHILD2,
    }
    result = collect("https://x.com/index.xml", lambda u: pages[u])
    assert result == ["https://x.com/a", "https://x.com/b"]


def test_collect_keeps_duplicates():
    # Duplicates must be preserved (not silently dropped) so they can be
    # detected and reported. The same page appearing in two child sitemaps
    # shows up twice.
    pages = {
        "https://x.com/index.xml": INDEX,
        "https://x.com/sm1.xml": CHILD1,
        "https://x.com/sm2.xml": CHILD1,  # same page twice
    }
    result = collect("https://x.com/index.xml", lambda u: pages[u])
    assert result == ["https://x.com/a", "https://x.com/a"]


def test_collect_skips_failing_child():
    def fetch_fn(u):
        if u == "https://x.com/sm2.xml":
            raise RuntimeError("boom")
        return {"https://x.com/index.xml": INDEX, "https://x.com/sm1.xml": CHILD1}[u]
    result = collect("https://x.com/index.xml", fetch_fn)
    assert result == ["https://x.com/a"]


def test_collect_depth_cap_does_not_raise():
    """A chain of index sitemaps deeper than MAX_DEPTH must not raise."""
    from sitemap_compare.sitemap import MAX_DEPTH

    def make_index(next_url):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<sitemap><loc>{next_url}</loc></sitemap>"
            "</sitemapindex>"
        )

    depth = MAX_DEPTH + 5  # build a chain deeper than the cap
    chain = {f"https://x.com/index_{i}.xml": make_index(f"https://x.com/index_{i+1}.xml")
             for i in range(depth)}
    # The last node is a urlset so a real leaf exists
    chain[f"https://x.com/index_{depth}.xml"] = (
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        "<url><loc>https://x.com/leaf</loc></url>"
        "</urlset>"
    )

    # Must not raise; result may be empty (capped) or contain the leaf if reachable
    result = collect("https://x.com/index_0.xml", lambda u: chain[u])
    assert isinstance(result, list)
