import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from sitemap_compare.fetcher import fetch, FetchError
from sitemap_compare.sitemap import collect
from sitemap_compare.compare import build_table, domain_label, duplicates_in
from sitemap_compare.render import table_to_html
from sitemap_compare.export import to_xlsx
from sitemap_compare.settings import load_settings, save_settings
from sitemap_compare.providers import resolve_fallback

load_dotenv()
# Resolve the (swappable) fetch fallback from the environment: Bright Data by
# default, a generic proxy, or none. See providers.py to add your own.
FALLBACK, FALLBACK_LABEL = resolve_fallback(os.environ)
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

st.set_page_config(page_title="Sitemap TLD Comparison", layout="wide")
st.title("Sitemap TLD Comparison")

# Prefill inputs from saved settings, once per session. Widget state lives in
# session_state keyed by widget key, so we seed those keys before the widgets
# are created; the widgets then read their values from session_state.
if "_loaded" not in st.session_state:
    _s = load_settings(SETTINGS_PATH)
    st.session_state.main_url = _s.get("main_url", "")
    _tlds = _s.get("tld_urls") or [""]
    st.session_state.tld_count = len(_tlds)
    for _i, _v in enumerate(_tlds):
        st.session_state[f"tld_{_i}"] = _v
    _aliases = _s.get("aliases") or []
    st.session_state.alias_count = max(1, len(_aliases))
    for _i in range(st.session_state.alias_count):
        _a = _aliases[_i] if _i < len(_aliases) else {}
        st.session_state[f"alias_treat_{_i}"] = _a.get("treat", "")
        st.session_state[f"alias_as_{_i}"] = _a.get("as", "")
    st.session_state._loaded = True

main_url = st.text_input(
    "Main sitemap URL", key="main_url", placeholder="https://www.example.com/sitemap.xml"
)

col_a, col_b = st.columns(2)
if col_a.button("+ Add TLD sitemap"):
    st.session_state.tld_count += 1
if col_b.button("- Remove TLD sitemap") and st.session_state.tld_count > 1:
    st.session_state.tld_count -= 1

tld_urls = []
for i in range(st.session_state.tld_count):
    tld_urls.append(st.text_input(f"TLD sitemap URL #{i + 1}", key=f"tld_{i}"))

# --- Path aliases: rewrite a translated TLD path so it lines up with the main path ---
with st.expander("Path aliases (optional)", expanded=any(
    st.session_state.get(f"alias_treat_{i}", "").strip()
    for i in range(st.session_state.alias_count)
)):
    st.caption(
        "Use when a page lives at a different path on a TLD. "
        "**Treat** a TLD path prefix **as** the matching main-site prefix. For example, "
        "treat `/blog/datos-web` as `/blog/web-data` aligns the Spanish blog with the main one."
    )
    ca, cb = st.columns(2)
    if ca.button("+ Add alias"):
        st.session_state.alias_count += 1
    if cb.button("- Remove alias") and st.session_state.alias_count > 1:
        st.session_state.alias_count -= 1
    for i in range(st.session_state.alias_count):
        c1, c2 = st.columns(2)
        c1.text_input("Treat (TLD path)", key=f"alias_treat_{i}", placeholder="/blog/datos-web")
        c2.text_input("as (main path)", key=f"alias_as_{i}", placeholder="/blog/web-data")

alias_pairs = [
    (st.session_state.get(f"alias_treat_{i}", ""), st.session_state.get(f"alias_as_{i}", ""))
    for i in range(st.session_state.alias_count)
]
alias_pairs = [(t, a) for t, a in alias_pairs if t.strip()]


def _save_current_settings():
    save_settings(
        SETTINGS_PATH,
        {
            "main_url": st.session_state.get("main_url", ""),
            "tld_urls": [st.session_state.get(f"tld_{i}", "") for i in range(st.session_state.tld_count)],
            "aliases": [
                {"treat": st.session_state.get(f"alias_treat_{i}", ""), "as": st.session_state.get(f"alias_as_{i}", "")}
                for i in range(st.session_state.alias_count)
                if st.session_state.get(f"alias_treat_{i}", "").strip()
            ],
        },
    )


def gather(url):
    """Collect page URLs for one sitemap, tracking the fetch method used."""
    methods = []

    def fetch_fn(u):
        res = fetch(u, fallback=FALLBACK, fallback_label=FALLBACK_LABEL)
        methods.append(res.method)
        return res.text

    pages = collect(url, fetch_fn)
    method = FALLBACK_LABEL if FALLBACK_LABEL in methods else "direct"
    return pages, method


run_col, reset_col = st.columns([1, 1])
compare_clicked = run_col.button("Compare", type="primary")
if reset_col.button("Reset"):
    try:
        os.remove(SETTINGS_PATH)
    except OSError:
        pass
    for _k in list(st.session_state.keys()):
        del st.session_state[_k]
    st.rerun()

if compare_clicked:
    if not main_url.strip():
        st.error("Enter the main sitemap URL.")
    else:
        _save_current_settings()
        sites = [(main_url.strip(), "main")] + [(u.strip(), f"TLD #{i+1}") for i, u in enumerate(tld_urls) if u.strip()]
        results = []
        problems = []
        with st.status("Fetching sitemaps...", expanded=True) as status:
            for url, label in sites:
                try:
                    pages, method = gather(url)
                    results.append(pages)
                    if pages:
                        st.write(f"✅ {label}: {len(pages)} URLs via {method} ({url})")
                    else:
                        st.write(f"⚠️ {label}: 0 URLs ({url})")
                        problems.append(f"{label} ({url}): 0 URLs found")
                except FetchError as e:
                    results.append([])
                    st.write(f"❌ {label}: {e}")
                    problems.append(f"{label} ({url}): {e}")
                except Exception as e:
                    results.append([])
                    st.write(f"❌ {label}: {type(e).__name__}: {e}")
                    problems.append(f"{label} ({url}): {type(e).__name__}: {e}")
            status.update(
                label="Done" if not problems else "Done with problems",
                state="complete" if not problems else "error",
            )

        if problems:
            st.warning(
                "Some sitemaps returned nothing:\n\n- "
                + "\n- ".join(problems)
                + "\n\nCheck the URL is exact (a typo like `.xm` instead of `.xml` "
                "will fail), that it points at a sitemap, and, if the site blocks "
                "direct requests, that a fallback provider is configured in `.env` (see README)."
            )

        main = (sites[0][0], results[0])
        tlds = [(sites[i][0], results[i]) for i in range(1, len(sites))]
        table = build_table(main, tlds, aliases=alias_pairs)
        html = table_to_html(table)

        # Duplicate URLs per site (same URL appearing more than once across that
        # site's sitemaps), kept in the data and surfaced here as (domain, url, count).
        dup_rows = []
        for i, (site_url, _label) in enumerate(sites):
            for url, count in duplicates_in(results[i]):
                dup_rows.append((domain_label(site_url), url, count))

        n_rows = len(table.matched_rows) + len(table.orphan_rows)
        st.subheader("Result")
        st.caption(
            f"{len(table.matched_rows)} main-site pages (aligned with the TLD where "
            f"a matching path exists) + {len(table.orphan_rows)} TLD-only pages at the end."
        )

        # Copy button + table live in ONE component (the button's JS must reach the
        # table in the same iframe). Clicking selects the table and copies it as rich
        # HTML, so a paste into Excel keeps the columns. Render-only (no raw-HTML dump,
        # which froze the tab on large sitemaps). Height scales with row count, capped.
        height = min(820, max(220, (n_rows + 1) * 30 + 70))
        copy_component = f"""
<button id="copybtn" onclick="copyTable()"
  style="margin:0 0 8px 0;padding:8px 14px;font-size:14px;font-weight:600;color:#fff;
         background:#0b57d0;border:none;border-radius:6px;cursor:pointer">
  📋 Copy table
</button>
{html}
<script>
function copyTable() {{
  var btn = document.getElementById('copybtn');
  var tbl = document.getElementById('smc-table');
  var sel = window.getSelection();
  sel.removeAllRanges();
  var range = document.createRange();
  range.selectNode(tbl);
  sel.addRange(range);
  var ok = false;
  try {{ ok = document.execCommand('copy'); }} catch (e) {{ ok = false; }}
  sel.removeAllRanges();
  btn.textContent = ok ? '✅ Copied! Paste into Excel' : '⚠️ Select the table and press Ctrl+C';
  setTimeout(function() {{ btn.textContent = '📋 Copy table'; }}, 2500);
}}
</script>
"""
        components.html(copy_component, height=height, scrolling=True)

        st.download_button(
            "⬇️ Download XLSX",
            data=to_xlsx(table, dup_rows),
            file_name="sitemap-comparison.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        if dup_rows:
            st.subheader(f"⚠️ Duplicates found ({len(dup_rows)})")
            st.caption(
                "URLs listed more than once within a single site's sitemap(s). "
                "They are kept in the data above; this panel reports them."
            )
            st.dataframe(
                [{"Site": s, "URL": u, "Count": c} for s, u, c in dup_rows],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("✅ No duplicate URLs found.")
