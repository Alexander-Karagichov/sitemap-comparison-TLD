import io

from openpyxl import Workbook

from .compare import Table


def to_xlsx(table: Table, duplicate_rows) -> bytes:
    """Serialize the comparison to an XLSX workbook (bytes).

    Sheet "Comparison": header row + matched rows + orphan rows.
    Sheet "Duplicates": Site / URL / Count for every duplicate found.
    ``duplicate_rows`` is an iterable of (site, url, count) tuples.
    """
    wb = Workbook()

    comparison = wb.active
    comparison.title = "Comparison"
    comparison.append(table.headers)
    for row in table.matched_rows:
        comparison.append(row)
    for row in table.orphan_rows:
        comparison.append(row)

    duplicates = wb.create_sheet("Duplicates")
    duplicates.append(["Site", "URL", "Count"])
    for site, url, count in duplicate_rows:
        duplicates.append([site, url, count])

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
