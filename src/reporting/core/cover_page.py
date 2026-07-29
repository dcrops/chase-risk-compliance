from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path


def build_cover_page(
    report_title: str,
    organisation_name: str,
    review_period: str,
    logo_path: str | Path | None = None,
    subtitle: str = "Payroll Risk & Evidence Review",
    prepared_as_at: str | None = None,
    confidentiality_label: str = "Confidential",
) -> str:
    prepared = prepared_as_at or date.today().strftime("%d %b %Y")

    logo_html = ""
    if logo_path:
        logo_html = (
            f'<img src="{escape(str(logo_path))}" '
            f'alt="Chase Risk & Compliance" class="cover-logo">'
        )

    return f"""
<div class="cover-page">
  <div class="cover-brand">
    {logo_html}
  </div>

  <div class="cover-kicker">{escape(subtitle)}</div>
  <div class="cover-title">{escape(report_title)}</div>

  <div class="cover-meta-card">
    <div class="cover-meta-row">
      <span class="cover-meta-label">Organisation</span>
      <span class="cover-meta-value">{escape(organisation_name)}</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Review period</span>
      <span class="cover-meta-value">{escape(review_period)}</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Prepared as at</span>
      <span class="cover-meta-value">{escape(prepared)}</span>
    </div>
  </div>

  <div class="cover-confidentiality">{escape(confidentiality_label)}</div>
</div>
""".strip()