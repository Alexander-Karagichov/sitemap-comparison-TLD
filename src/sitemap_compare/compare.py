from collections import Counter
from dataclasses import dataclass, field
from urllib.parse import urlsplit


def duplicates_in(urls):
    """URLs that appear more than once in a site's list, as (url, count),
    sorted by url. Used to report duplicates without dropping them."""
    counts = Counter(urls)
    return sorted((u, c) for u, c in counts.items() if c > 1)


def path_of(url: str) -> str:
    parts = urlsplit(url.strip())
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"
    return path


def domain_label(url: str) -> str:
    host = urlsplit(url.strip()).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _norm_seg(seg: str) -> str:
    """Normalize an alias path fragment: ensure one leading slash, no trailing."""
    seg = (seg or "").strip()
    if not seg:
        return ""
    if not seg.startswith("/"):
        seg = "/" + seg
    if len(seg) > 1:
        seg = seg.rstrip("/")
    return seg


def apply_aliases(path: str, rules) -> str:
    """Rewrite a path by prefix-matching alias rules so a translated TLD path
    lines up with the main path. ``rules`` is an iterable of (treat, as) pairs.

    A rule matches when the path equals ``treat`` or starts with ``treat`` + "/",
    and only that leading part is replaced (the rest is kept)."""
    for treat, repl in rules:
        t = _norm_seg(treat)
        r = _norm_seg(repl)
        if not t:
            continue
        if path == t:
            path = r
        elif path.startswith(t + "/"):
            path = r + path[len(t):]
    return path


@dataclass
class Table:
    headers: list[str] = field(default_factory=list)
    matched_rows: list[list[str]] = field(default_factory=list)
    orphan_rows: list[list[str]] = field(default_factory=list)


def _key_map(urls, aliases):
    """{alignment_key: original_url}, first occurrence wins. The key is the
    alias-rewritten path so translated TLD paths group with the main path."""
    m = {}
    for u in urls:
        key = apply_aliases(path_of(u), aliases)
        if key not in m:
            m[key] = u
    return m


def build_table(main, tlds, aliases=None):
    aliases = aliases or []
    main_label, main_urls = main
    main_map = _key_map(main_urls, aliases)
    tld_maps = [_key_map(urls, aliases) for _, urls in tlds]

    headers = [domain_label(main_label)] + [domain_label(lbl) for lbl, _ in tlds]

    matched_rows = []
    for p in sorted(main_map):
        row = [main_map[p]] + [tm.get(p, "") for tm in tld_maps]
        matched_rows.append(row)

    orphan_paths = set()
    for tm in tld_maps:
        for p in tm:
            if p not in main_map:
                orphan_paths.add(p)

    orphan_rows = []
    for p in sorted(orphan_paths):
        row = [""] + [tm.get(p, "") for tm in tld_maps]
        orphan_rows.append(row)

    return Table(headers=headers, matched_rows=matched_rows, orphan_rows=orphan_rows)
