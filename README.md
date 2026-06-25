<div align="center">

# 🗺️ Sitemap TLD Comparison

**Stop diffing sitemaps in side-by-side browser tabs. Line them up automatically.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)](https://www.python.org/)
[![Powered by Bright Data](https://img.shields.io/badge/Powered%20by-Bright%20Data-orange?style=for-the-badge)](https://brightdata.com/?utm_source=sitemap-comparison-os)
[![UI: Streamlit](https://img.shields.io/badge/UI-Streamlit-red?style=for-the-badge)](https://streamlit.io/)

Paste your main site's sitemap and the sitemaps of its country/language variants. Get a **side-by-side table** that lines up every page with its counterpart on each other domain (same path, same row), ready to **copy into Excel** or **download as XLSX**.

[The Problem](#-the-problem) · [The Solution](#-the-solution) · [What You Get](#-what-you-get) · [Quick Start](#-quick-start) · [How It Works](#-how-it-works) · [Path Aliases](#-path-aliases) · [Configuration](#️-configuration)

</div>

---

> 🌐 **Works great with [Bright Data](https://brightdata.com/?utm_source=sitemap-comparison-os).** Sitemaps on big sites are often behind bot protection. When a plain request gets blocked, the app falls back to an unlocker so the fetch still succeeds. The default is Bright Data's [Web Unlocker](https://docs.brightdata.com/scraping-automation/web-unlocker/introduction), and it's fully swappable (see [Fetch Providers](#-fetch-providers)). [Get a Bright Data key →](https://brightdata.com/?utm_source=sitemap-comparison-os)

---

## 😱 The Problem

Your company runs one site across a dozen ccTLDs (`.com`, `.cn`, `.es`, `.de`), and you need to know which pages exist where.

```
You: *Opens example.com/sitemap.xml in one tab*
You: *Opens example.de/sitemap.xml in another*
You: *Ctrl+F a path in tab 1… switch… Ctrl+F in tab 2…*
You: *Copies matches into a spreadsheet, one row at a time*
You: *Gives up after 200 of 5,000 URLs*

Meanwhile:
  ✗ The .de site is missing 40 product pages nobody noticed
  ✗ A translated blog path never lined up, so it looks "missing"
  ✗ The same URL is listed twice in one sitemap and skews your counts
```

**Comparing sitemaps across domains by hand is slow, error-prone, and never finished.**

---

## ✨ The Solution

```
Paste the sitemap URLs  →  Click "Compare"  →  Copy the table / Download XLSX
```

The app scrapes **only the sitemaps** (recursing into sitemap-index files), then aligns every page by its URL path so matching pages sit on the same row.

| Feature | What it does |
|---|---|
| 🌍 **Multi-TLD comparison** | One column per domain; pages sharing a path align on the same row |
| 🧭 **Sitemap-index recursion** | Follows `<sitemapindex>` into every child sitemap automatically |
| 🖼️ **Asset filtering** | Ignores image-extension `<image:loc>` entries (`.svg`/`.png`), so you get real pages only |
| 🔀 **Path aliases** | Map a translated TLD path (`/blog/datos-web`) to the main one (`/blog/web-data`) so localized URLs still line up |
| 📋 **Copy to Excel** | One click copies the table as rich HTML, ready to paste straight into a spreadsheet with columns intact |
| ⬇️ **XLSX export** | Download a workbook with **Comparison** + **Duplicates** sheets |
| 🔁 **Duplicate detection** | Flags any URL listed more than once within a site, in its own panel |
| 💾 **Saved settings** | Remembers your sitemap URLs and alias rules between runs; **Reset** clears everything |
| 🛡️ **Reliable fetching** | Direct HTTP first; an optional, swappable unlocker fallback (Bright Data by default) for blocked sites |

---

## 💡 What You Get

A clean, copy-pasteable table with one column per domain and one row per page path:

| example.com | example.de |
|---|---|
| https://example.com/ | https://www.example.de/ |
| https://example.com/products/widgets | https://www.example.de/products/widgets |
| https://example.com/pricing | *(blank: missing on .de)* |
| *(blank: TLD-only)* | https://www.example.de/karriere |

- **Matched rows** come first: every main-site page, with the TLD's URL beside it (or blank where it has no counterpart).
- **TLD-only pages** land in rows at the **very end**, with the main column left blank, so you instantly see coverage gaps in both directions.
- **Duplicates** (the same URL listed twice within a site) are kept in the data and reported separately, never silently dropped.

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/Alexander-Karagichov/sitemap-comparison-TLD.git
cd sitemap-comparison-TLD
```

### 2. Install

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure (optional)

```bash
cp .env.example .env
# Add a Bright Data API token only if you need the fallback (see Configuration)
```

### 4. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501), paste your main sitemap URL and one or more TLD sitemap URLs, and click **Compare**. Then **📋 Copy table** or **⬇️ Download XLSX**.

For a full walkthrough of every feature, see the [Usage Guide](USAGE.md).

---

## 📖 How It Works

```
1. Fetch ...... Direct HTTP GET first; if it's blocked, use the Bright Data Web Unlocker
2. Parse ...... Detect <urlset> vs <sitemapindex>; recurse indexes; keep pages, drop image assets
3. Align ...... Key each URL by its path (plus your alias rules); group across all domains
4. Report ..... Main-site rows first, TLD-only rows at the end; duplicates in their own panel
```

XML is parsed with [`defusedxml`](https://pypi.org/project/defusedxml/) to stay safe against malicious remote sitemaps (XXE / billion-laughs). All logic is unit-tested (`python -m pytest`).

---

## 🔀 Path Aliases

Sometimes the "same" page lives at a **different path** on a TLD, usually because the slug is translated:

```
main:  https://example.com/blog/web-data/how-to-scrape
.es:   https://example.es/blog/datos-web/how-to-scrape
```

Open **Path aliases** and add a rule:

| Treat (TLD path) | as (main path) |
|---|---|
| `/blog/datos-web` | `/blog/web-data` |

Now the Spanish URL is rewritten to `/blog/web-data/how-to-scrape` for matching and lines up on the same row as the main page. Matching is by **path prefix**, the original URLs are still shown, and you can add as many rules as you need. Aliases are saved with your settings.

---

## ⚙️ Configuration

The app tries a **direct** fetch first, so for sitemaps that aren't bot-protected it works with **no configuration at all**. Settings only matter for the fallback used on blocked sites, and they live in `.env` (copy from `.env.example`):

| Variable | Purpose |
|---|---|
| `FETCH_PROVIDER` | Which fallback to use: `brightdata`, `proxy`, or `none`. Blank auto-detects |
| `BRIGHTDATA_API_TOKEN` | Token for the Bright Data Web Unlocker fallback |
| `BRIGHTDATA_ZONE` | Your Bright Data Web Unlocker zone name |
| `FETCH_PROXY_URL` | HTTP(S) proxy for the `proxy` fallback, e.g. `http://user:pass@host:port` |

> `.env` and your saved `settings.json` are git-ignored, so tokens and inputs never get committed.

---

## 🔄 Fetch Providers

The fallback is **not locked to Bright Data**. The fetcher itself is vendor-neutral; a provider is just a callable `(url) -> str` that returns the sitemap XML. Two are built in:

- **`brightdata`** (default): the Bright Data Web Unlocker REST API. Set `BRIGHTDATA_API_TOKEN` and `BRIGHTDATA_ZONE`.
- **`proxy`**: routes the request through any HTTP(S) proxy or proxy-based unlocker (ScraperAPI, Oxylabs, Bright Data proxy mode, your own). Set `FETCH_PROXY_URL`.

Pick one with `FETCH_PROVIDER`, or leave it blank to auto-detect. The status line after a fetch shows which one was used (`via direct`, `via brightdata`, `via proxy`).

Want a different service? Add a callable to the `PROVIDERS` registry in [`src/sitemap_compare/providers.py`](src/sitemap_compare/providers.py) and select it with `FETCH_PROVIDER`. No other code changes needed.

---

## 📜 License

Released under the [MIT License](LICENSE).

---

<div align="center">

✨ **Powered by [Bright Data](https://brightdata.com/?utm_source=sitemap-comparison-os), the world's leading web data platform.**

</div>
