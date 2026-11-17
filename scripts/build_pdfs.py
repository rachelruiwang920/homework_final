"""用系統瀏覽器把限頁報告印成 PDF。實驗本身不依賴這個步驟。"""

from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[1]
CHROME = "/usr/bin/google-chrome"


def markdown_to_html(text: str) -> str:
    blocks = []
    for raw in text.strip().split("\n\n"):
        chunk = raw.strip()
        if not chunk:
            continue
        if chunk.startswith("# "):
            blocks.append(f"<h1>{html.escape(chunk[2:].strip())}</h1>")
            continue
        if chunk.startswith("## "):
            blocks.append(f"<h2>{html.escape(chunk[3:].strip())}</h2>")
            continue
        lines = [html.escape(line.strip()) for line in chunk.splitlines() if line.strip()]
        if lines and all(line.startswith("https://") for line in lines):
            items = "".join(f"<li>{line}</li>" for line in lines)
            blocks.append(f"<ul class='urls'>{items}</ul>")
            continue
        blocks.append(f"<p>{'<br>'.join(lines)}</p>")
    body = "\n".join(blocks)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<style>
@page {{ size: A4; margin: 12mm 14mm; }}
html, body {{
  font-family: "WenQuanYi Micro Hei", "Droid Sans Fallback", sans-serif;
  font-size: 10pt;
  line-height: 1.38;
  color: #1c1917;
}}
h1 {{ font-size: 14pt; line-height: 1.25; margin: 0 0 8px; font-weight: 600; }}
h2 {{ font-size: 11.5pt; margin: 8px 0 4px; font-weight: 600; }}
p {{ margin: 0 0 7px; }}
ul.urls {{ margin: 2px 0 0; padding-left: 1.1em; font-size: 8pt; line-height: 1.28; }}
li {{ margin: 0; word-break: break-all; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def render(markdown_path: Path, pdf_path: Path, max_pages: int, compact: bool = False) -> int:
    page = markdown_to_html(markdown_path.read_text(encoding="utf-8"))
    if compact:
        page = page.replace("font-size: 10pt;", "font-size: 9pt;", 1)
        page = page.replace("line-height: 1.38;", "line-height: 1.28;", 1)
        page = page.replace("margin: 12mm 14mm;", "margin: 10mm 12mm;", 1)
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(page, encoding="utf-8")
    pdf_path.unlink(missing_ok=True)
    command = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.resolve().as_uri(),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0 or not pdf_path.is_file():
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(f"瀏覽器無法印出 {pdf_path.name}")
    pages = len(PdfReader(str(pdf_path)).pages)
    if pages > max_pages:
        raise SystemExit(f"{pdf_path.name} 有 {pages} 頁，超過 {max_pages} 頁")
    return pages


def main() -> int:
    summary_pages = render(
        REPO / "reports" / "01-critical-summary.md",
        REPO / "reports" / "01-critical-summary.pdf",
        1,
    )
    analysis_pages = render(
        REPO / "reports" / "03-analysis.md",
        REPO / "reports" / "03-analysis.pdf",
        2,
    )
    brief_pages = render(
        REPO / "final-brief.md",
        REPO / "reports" / "final-brief.pdf",
        1,
        compact=True,
    )
    if summary_pages != 1 or brief_pages != 1:
        raise SystemExit(
            f"摘要或簡報不是 1 頁：summary={summary_pages} brief={brief_pages}"
        )
    print(f"critical-summary pages={summary_pages}")
    print(f"analysis pages={analysis_pages}")
    print(f"final-brief pages={brief_pages}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
