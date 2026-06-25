# Usage Guide

A walkthrough of running the app and using every feature. For install details and
the project overview, see the [README](README.md).

## Run it

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Wait for the terminal to print `Local URL: http://localhost:8501`, then open that
address in your browser.

## 1. Enter your sitemaps

- **Main sitemap URL**: paste the sitemap of your primary site. A sitemap index
  (a file that points to other sitemaps) works too, the app follows it.
  Example: `https://www.example.com/sitemap.xml`
- **TLD sitemaps**: click **+ Add TLD sitemap** and paste the sitemap URL for each
  country or language variant. Add as many as you need.
  Example: `https://www.example.de/sitemap.xml`

Use the exact URL, including the `.xml` ending. A small typo (for example `.xm`)
will fail to fetch.

## 2. Path aliases (optional)

Use this when the same page sits at a different path on a TLD, usually because the
slug is translated. Open **Path aliases** and add a rule:

| Treat (TLD path) | as (main path) |
|---|---|
| `/blog/datos-web` | `/blog/web-data` |

With that rule, `https://www.example.es/blog/datos-web/how-to-scrape` is matched as
`/blog/web-data/how-to-scrape`, so it lands on the same row as the main page. The
original URLs are still shown in the table. Matching is by **path prefix**, and you
can add as many rules as you need.

## 3. Click Compare

The app fetches each sitemap and shows a status line per site, for example:

```
main: 5,400 URLs via direct (https://www.example.com/sitemap.xml)
TLD #1: 3,100 URLs via direct (https://www.example.de/sitemap.xml)
```

`via direct` means a plain request worked. `via brightdata` or `via proxy` means the
site blocked the direct request and the configured fallback was used (see
[Fetch providers](#fetch-providers-for-blocked-sitemaps)). If a sitemap returns
nothing, a yellow warning lists which URL failed and why.

## 4. Read the results table

- Each **column** is one domain (the bare host, `www.` removed).
- Each **row** is one page path.
- **Matched rows** come first: every page on the main site, with the TLD's URL beside
  it, or a blank cell where that TLD has no matching page.
- **TLD-only rows** come at the very end: pages that exist on a TLD but not on the main
  site, with the main column left blank.

So a blank cell means "this page is missing on that domain," which is exactly what you
are looking for.

## 5. Copy or download

- **Copy table**: click the button above the table. It copies the table as rich HTML,
  so you can paste straight into Excel or Google Sheets with the columns intact. If your
  browser blocks the copy, select the table and press Ctrl+C instead.
- **Download XLSX**: downloads an Excel workbook with two sheets, **Comparison** (the
  full table) and **Duplicates** (the report below).

## 6. Duplicates panel

If a URL is listed more than once within a single site (for example the same page in
two child sitemaps), it appears in the **Duplicates found** panel with the site, the
URL, and how many times it was seen. Duplicates are never silently dropped. If there
are none, the app says so.

## Saved settings and Reset

Your main URL, TLD URLs, and alias rules are saved automatically when you click
**Compare**, to a git-ignored `settings.json`, and are filled in for you next time you
open the app. Click **Reset** to clear every input and delete that file. Results are
never saved.

## Fetch providers (for blocked sitemaps)

The app always tries a **direct** request first, so for sitemaps that are not
bot-protected it needs no configuration at all. A fallback is only used when a site
blocks the direct request. Configure it in `.env` (copy from `.env.example`):

| Variable | Purpose |
|---|---|
| `FETCH_PROVIDER` | Which fallback to use: `brightdata`, `proxy`, or `none`. Blank auto-detects |
| `BRIGHTDATA_API_TOKEN` | Token for the Bright Data Web Unlocker fallback |
| `BRIGHTDATA_ZONE` | Your Bright Data Web Unlocker zone name |
| `FETCH_PROXY_URL` | HTTP(S) proxy for the `proxy` fallback, for example `http://user:pass@host:port` |

The `proxy` option works with any proxy-based unlocker (ScraperAPI, Oxylabs, Bright
Data proxy mode, your own). To add a different service entirely, register a callable in
the `PROVIDERS` dictionary in `src/sitemap_compare/providers.py` and select it with
`FETCH_PROVIDER`.

## Tips

- **Scope a huge site**: a sitemap index can expand into tens of thousands of pages. To
  compare a specific section, paste a single child sitemap instead of the index, for
  example `https://www.example.com/page-sitemap.xml`.
- **Matching is exact**: paths are compared exactly, including trailing slashes and any
  query string. Use path aliases for intentional differences.
- **Image assets are ignored**: image-extension entries (`.svg`, `.png`) inside a
  sitemap are not treated as pages.

## Troubleshooting

- **A site shows 0 URLs**: check the URL is exact and ends in `.xml`, that it points at
  a sitemap, and, if the site blocks direct requests, that a fallback provider is set in
  `.env`.
- **Large sitemaps**: the table can be long, but it will not freeze the tab. Use a child
  sitemap to narrow the scope if you prefer.
- **Stopping the app**: press Ctrl+C in the terminal. Wait until the `Local URL` line has
  printed before interrupting, so startup finishes cleanly.
