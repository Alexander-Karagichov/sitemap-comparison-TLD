from sitemap_compare.compare import (
    path_of,
    domain_label,
    build_table,
    Table,
    duplicates_in,
    apply_aliases,
)


def test_apply_aliases_prefix_rewrite():
    rules = [("/blog/datos-web", "blog/web-data")]  # 'as' without leading slash
    assert (
        apply_aliases("/blog/datos-web/web-scraping-vs-api", rules)
        == "/blog/web-data/web-scraping-vs-api"
    )


def test_apply_aliases_exact_match():
    assert apply_aliases("/blog/datos-web", [("/blog/datos-web", "/blog/web-data")]) == "/blog/web-data"


def test_apply_aliases_no_match_unchanged():
    # Prefix only: the text appears deeper in the path, so it is NOT rewritten.
    assert apply_aliases("/x/blog/datos-web", [("/blog/datos-web", "/blog/web-data")]) == "/x/blog/datos-web"


def test_build_table_aligns_via_alias():
    main = ("https://brightdata.com/", ["https://brightdata.com/blog/web-data/x"])
    tld = ("https://brightdata.es/", ["https://brightdata.es/blog/datos-web/x"])
    rules = [("/blog/datos-web", "/blog/web-data")]
    t = build_table(main, [tld], aliases=rules)
    # Without the alias these would be two separate rows; with it they align.
    assert t.matched_rows == [
        ["https://brightdata.com/blog/web-data/x", "https://brightdata.es/blog/datos-web/x"]
    ]
    assert t.orphan_rows == []


def test_duplicates_in_counts_repeats():
    urls = [
        "https://x.com/a",
        "https://x.com/b",
        "https://x.com/a",   # dup
        "https://x.com/a",   # dup again -> count 3
        "https://x.com/b",   # dup -> count 2
    ]
    # Returns (url, count) for urls seen more than once, sorted by url.
    assert duplicates_in(urls) == [("https://x.com/a", 3), ("https://x.com/b", 2)]


def test_duplicates_in_empty_when_unique():
    assert duplicates_in(["https://x.com/a", "https://x.com/b"]) == []


def test_path_of_strips_scheme_and_host():
    assert path_of("https://brightdata.com/proxy-types/residential") == "/proxy-types/residential"


def test_path_of_keeps_query():
    assert path_of("https://brightdata.com/p?a=1") == "/p?a=1"


def test_path_of_preserves_trailing_slash():
    assert path_of("https://brightdata.com/proxy/") == "/proxy/"


def test_domain_label_strips_www():
    assert domain_label("https://www.bright.cn/x") == "bright.cn"


def test_domain_label_no_www():
    assert domain_label("https://brightdata.com/") == "brightdata.com"


def test_build_table_matches_by_path():
    main = ("https://brightdata.com/", ["https://brightdata.com/a", "https://brightdata.com/b"])
    tld = ("https://www.bright.cn/", ["https://www.bright.cn/a"])
    t = build_table(main, [tld])
    assert t.headers == ["brightdata.com", "bright.cn"]
    assert t.matched_rows == [
        ["https://brightdata.com/a", "https://www.bright.cn/a"],
        ["https://brightdata.com/b", ""],
    ]
    assert t.orphan_rows == []


def test_build_table_orphans_at_end_with_blank_main():
    main = ("https://brightdata.com/", ["https://brightdata.com/a"])
    tld = ("https://www.bright.cn/", ["https://www.bright.cn/a", "https://www.bright.cn/only-cn"])
    t = build_table(main, [tld])
    assert t.matched_rows == [["https://brightdata.com/a", "https://www.bright.cn/a"]]
    assert t.orphan_rows == [["", "https://www.bright.cn/only-cn"]]


def test_build_table_shared_orphan_one_row():
    main = ("https://brightdata.com/", [])
    tld1 = ("https://www.bright.cn/", ["https://www.bright.cn/x"])
    tld2 = ("https://bright.de/", ["https://bright.de/x"])
    t = build_table(main, [tld1, tld2])
    assert t.headers == ["brightdata.com", "bright.cn", "bright.de"]
    assert t.matched_rows == []
    assert t.orphan_rows == [["", "https://www.bright.cn/x", "https://bright.de/x"]]
