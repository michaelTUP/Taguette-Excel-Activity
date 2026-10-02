"""Rebuild Taguette-Excel-Activity.pdf from index.html.

Run this after you edit the page, then commit the new PDF:
    python tools/make-pdf.py

Needs Python with Playwright (pip install playwright) and Google Chrome.
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
OUT = ROOT / "Taguette-Excel-Activity.pdf"

FOOTER = """<div style="width:100%;font:8px 'Segoe UI',Arial,sans-serif;color:#7A8098;padding:0 14mm;display:flex;justify-content:space-between">
<span>Practice Activity: Taguette and Excel PivotTables &middot; TEM 603</span>
<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>"""

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(color_scheme="light", viewport={"width": 1200, "height": 900})
    page.goto(PAGE.as_uri(), wait_until="networkidle")
    # open the transcripts and answer keys, and load every picture now
    page.evaluate("""() => {
        document.querySelectorAll('details').forEach(d => d.open = true);
        document.querySelectorAll('.shot img').forEach(i => i.loading = 'eager');
    }""")
    page.wait_for_function("() => [...document.querySelectorAll('.shot img')].every(i => i.complete && i.naturalWidth > 0)")
    page.evaluate("document.fonts.ready")
    page.emulate_media(media="print")
    page.pdf(path=str(OUT), format="A4", print_background=True,
             margin={"top": "14mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
             display_header_footer=True, header_template="<span></span>", footer_template=FOOTER)
    browser.close()

print(f"Wrote {OUT.name} ({OUT.stat().st_size / 1e6:.1f} MB)")
