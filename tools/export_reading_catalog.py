#!/usr/bin/env python3
"""Export a searchable, offline HTML reading list from an installed Lastbook pack.

Usage: python3 tools/export_reading_catalog.py --data /path/to/LastbookData --output books.html
This is a list of titles, not a download service or permission to redistribute files.
"""
import argparse
import html
import json
from pathlib import Path

READING_KINDS = {"pdf", "html", "pptx"}

def export(catalog_path, output_path):
    records = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("catalog.json must contain a list")
    entries = []
    for record in records:
        if not isinstance(record, dict) or record.get("kind") not in READING_KINDS:
            continue
        title = str(record.get("title") or "").strip()
        if title:
            entries.append((str(record.get("collection") or "Other"), title,
                            str(record["kind"]).upper(), str(record.get("publisher") or "")))
    entries.sort(key=lambda row: (row[0].casefold(), row[1].casefold()))
    rows = "\n".join("<tr>" + "".join("<td>" + html.escape(field, quote=True) + "</td>"
                                      for field in row) + "</tr>" for row in entries)
    page = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lastbook reading catalog</title>
<style>
body{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem}
input{font:inherit;padding:.6rem;width:min(100%,35rem);box-sizing:border-box}
table{width:100%;border-collapse:collapse;margin-top:1rem}
th,td{text-align:left;padding:.6rem;border-bottom:1px solid #8885}
tr[hidden]{display:none}
@media(max-width:650px){th:last-child,td:last-child{display:none}}
</style>
<h1>Lastbook reading catalog</h1>
<p>Titles from one installed library pack. This is a listing, not a download service. No network connection is used.</p>
<label for="q">Search titles and collections</label>
<input id="q" type="search" placeholder="Search"><p id="count"></p>
<table><thead><tr><th>Collection</th><th>Title</th><th>Type</th><th>Publisher</th></tr></thead>
<tbody>""" + rows + """</tbody></table>
<script>
const q=document.getElementById('q'),rs=[...document.querySelectorAll('tbody tr')],count=document.getElementById('count');
function filter(){const v=q.value.toLocaleLowerCase();let n=0;
for(const r of rs){r.hidden=!r.textContent.toLocaleLowerCase().includes(v);if(!r.hidden)n++}
count.textContent=n+' titles';}
q.addEventListener('input',filter);filter();
</script></html>"""
    Path(output_path).write_text(page, encoding="utf-8")
    return len(entries)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True, help="Folder containing library-data/catalog.json")
    parser.add_argument("--output", type=Path, required=True, help="Output HTML file")
    args = parser.parse_args()
    print(f"Exported {export(args.data / 'library-data' / 'catalog.json', args.output)} titles to {args.output}")

if __name__ == "__main__":
    main()
