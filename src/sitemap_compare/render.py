from html import escape
from .compare import Table

# Light, self-contained theme so the table is readable regardless of the host
# page's (dark) theme, and pastes cleanly into Excel. Scoped under .smc so it
# can't leak into the surrounding app.
_STYLE = (
    "<style>"
    "body{margin:0}"
    ".smc{background:#ffffff;color:#111;"
    "font-family:Arial,Helvetica,sans-serif;font-size:13px}"
    ".smc table{border-collapse:collapse;width:100%}"
    ".smc th,.smc td{border:1px solid #cccccc;padding:6px 10px;"
    "text-align:left;vertical-align:top}"
    ".smc th{background:#f2f2f2;position:sticky;top:0}"
    ".smc a{color:#0b57d0;word-break:break-all}"
    "</style>"
)


def _cell(value: str) -> str:
    if not value:
        return "<td></td>"
    safe = escape(value)
    if value.lower().startswith("http://") or value.lower().startswith("https://"):
        # target=_blank so a click opens a new tab instead of navigating this
        # component's iframe to a page that refuses to be framed (which would
        # replace the whole table with a "refused to connect" error).
        return f'<td><a href="{safe}" target="_blank" rel="noopener noreferrer">{safe}</a></td>'
    return f"<td>{safe}</td>"


def table_to_html(table: Table) -> str:
    parts = [_STYLE, '<div class="smc"><table id="smc-table" border="1" cellspacing="0" cellpadding="4">']
    parts.append("<tr>" + "".join(f"<th>{escape(h)}</th>" for h in table.headers) + "</tr>")
    for row in table.matched_rows:
        parts.append("<tr>" + "".join(_cell(c) for c in row) + "</tr>")
    for row in table.orphan_rows:
        parts.append("<tr>" + "".join(_cell(c) for c in row) + "</tr>")
    parts.append("</table></div>")
    return "".join(parts)
