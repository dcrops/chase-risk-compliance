from __future__ import annotations

import argparse
from pathlib import Path

import markdown
from weasyprint import HTML, CSS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "clients"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Pilot Report</title>
  <style>
    {css}
  </style>
</head>
<body>
  <main class="report-container pilot-report">
    {body}
  </main>
</body>
</html>
"""


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def build_html_from_markdown(md_text: str, css_text: str) -> str:
    body_html = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "sane_lists", "toc"],
    )
    return HTML_TEMPLATE.format(css=css_text, body=body_html)


def render_pilot_report(client: str, pilot: str) -> tuple[Path, Path]:
    outputs_dir = DATA_ROOT / client / pilot / "outputs"

    md_path = outputs_dir / "pilot_report.md"
    html_path = outputs_dir / "pilot_report.html"
    pdf_path = outputs_dir / "pilot_report.pdf"

    candidate_css_paths = [
        PROJECT_ROOT / "src" / "reporting" / "assets" / "crc_report.css",
        PROJECT_ROOT / "src" / "reporting" / "crc_report.css",
        PROJECT_ROOT / "reporting" / "assets" / "crc_report.css",
        PROJECT_ROOT / "reporting" / "crc_report.css",
    ]

    css_path = next((p for p in candidate_css_paths if p.exists()), None)

    if css_path is None:
        matches = list(PROJECT_ROOT.rglob("crc_report.css"))
        if matches:
            css_path = matches[0]
            print(f"[INFO] Auto-detected CSS at: {css_path}")
        else:
            raise FileNotFoundError("Could not find crc_report.css anywhere under the project root.")

    md_text = load_text(md_path)
    css_text = load_text(css_path)

    html_text = build_html_from_markdown(md_text, css_text)
    html_path.write_text(html_text, encoding="utf-8")

    HTML(string=html_text, base_url=str(PROJECT_ROOT)).write_pdf(
        pdf_path,
        stylesheets=[CSS(string=css_text)],
    )

    print(f"[OK] Wrote HTML: {html_path}")
    print(f"[OK] Wrote PDF:  {pdf_path}")

    return html_path, pdf_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render pilot_report.md to HTML and PDF.")
    parser.add_argument("--client", required=True, help="Client code, e.g. CLT_KAGGLE_TEST")
    parser.add_argument("--pilot", required=True, help="Pilot code, e.g. PILOT_004_CONTROLLED_CLEAN")
    args = parser.parse_args()

    render_pilot_report(client=args.client, pilot=args.pilot)


if __name__ == "__main__":
    main()