# defusedxml hardens parsing of untrusted remote XML against XXE and
# billion-laughs entity-expansion attacks.
from defusedxml.ElementTree import fromstring

MAX_DEPTH = 20


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def parse(xml_text: str):
    root = fromstring(xml_text.strip())
    kind = "index" if _local(root.tag) == "sitemapindex" else "urlset"
    entry_tag = "sitemap" if kind == "index" else "url"
    locs = []
    # Only take the <loc> that is a DIRECT child of a <url>/<sitemap> entry.
    # This excludes extension elements like the image sitemap's <image:loc>
    # (which also ends in "loc" but points at .svg/.png assets, not pages).
    for entry in root:
        if _local(entry.tag) != entry_tag:
            continue
        for child in entry:
            if _local(child.tag) == "loc" and child.text:
                locs.append(child.text.strip())
                break
    return kind, locs


def collect(url: str, fetch_fn, _visited=None, _depth: int = 0) -> list[str]:
    if _depth > MAX_DEPTH:
        return []
    if _visited is None:
        _visited = set()
    if url in _visited:
        return []
    _visited.add(url)

    kind, locs = parse(fetch_fn(url))
    if kind == "urlset":
        return list(locs)

    # Sitemap index: recurse into children and flatten, PRESERVING duplicates
    # (the same page may legitimately appear in two child sitemaps, and we want
    # to surface that, not hide it). The _visited set still prevents re-fetching
    # the same sitemap, so genuine cycles can't loop forever.
    out = []
    for child in locs:
        try:
            out.extend(collect(child, fetch_fn, _visited, _depth + 1))
        except Exception:
            continue
    return out
