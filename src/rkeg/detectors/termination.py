from __future__ import annotations

from typing import Dict, List
import json

import pandas as pd

from rkeg.models import Finding, build_finding


DEFAULT_FINAL_PAY_DAYS_THRESHOLD = 7

TRUTHY_FLAG_VALUES = {"y", "yes", "true", "t", "1"}

BASIS_FLAGGED = "flagged_final_pay"
BASIS_LATEST_PAY = "latest_post_termination_pay"


def _pick_first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in cols:
            return cols[candidate.lower()]
    return None


def _truthy_flag_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin(TRUTHY_FLAG_VALUES)


def _term_001_final_pay_outside_threshold(
    rule: dict,
    datasets: Dict[str, pd.DataFrame],
) -> List[Finding]:
    terminations = datasets.get("terminations", pd.DataFrame())
    pay_events = datasets.get("pay_events", pd.DataFrame())

    if terminations.empty or pay_events.empty:
        return []

    if "employee_id" not in terminations.columns or "employee_id" not in pay_events.columns:
        return []

    term_date_col = _pick_first_existing_column(
        terminations,
        ["termination_date", "term_date", "end_date", "termination_effective_date"],
    )
    pay_date_col = _pick_first_existing_column(
        pay_events,
        ["pay_date", "payment_date", "event_date"],
    )

    if term_date_col is None or pay_date_col is None:
        return []

    term = terminations.copy()
    pay = pay_events.copy()

    term["employee_id"] = term["employee_id"].astype(str).str.strip()
    pay["employee_id"] = pay["employee_id"].astype(str).str.strip()

    term["_termination_date"] = pd.to_datetime(term[term_date_col], errors="coerce")
    pay["_pay_date"] = pd.to_datetime(pay[pay_date_col], errors="coerce")

    term = term[term["_termination_date"].notna()].copy()
    pay = pay[pay["_pay_date"].notna()].copy()

    if term.empty or pay.empty:
        return []

    final_pay_flag_col = _pick_first_existing_column(
        pay_events,
        ["is_final_pay", "final_pay", "final_pay_flag"],
    )

    if final_pay_flag_col is not None:
        pay["_is_final_pay"] = _truthy_flag_series(pay[final_pay_flag_col])
    else:
        pay["_is_final_pay"] = False

    merged = term.merge(
        pay[["employee_id", "_pay_date", "_is_final_pay"]],
        on="employee_id",
        how="left",
    )

    candidates = merged[merged["_pay_date"] >= merged["_termination_date"]].copy()

    if candidates.empty:
        return []

    group_keys = ["employee_id", "_termination_date"]

    # A pay event explicitly flagged as final is the defensible basis for final
    # pay timing. Where the extract carries no such flag on or after
    # termination, the latest post-termination pay is used as a lower-certainty
    # proxy and the basis is recorded in the evidence so a reviewer can see
    # which was used.
    flagged_pays = candidates[candidates["_is_final_pay"]].copy()

    proxy_basis = candidates.groupby(group_keys, as_index=False).agg(
        _final_pay_date=("_pay_date", "max"),
        _post_termination_pay_count=("_pay_date", "count"),
    )
    proxy_basis["_final_pay_basis"] = BASIS_LATEST_PAY
    proxy_basis["_flagged_final_pay_count"] = 0

    if flagged_pays.empty:
        final_pay = proxy_basis
    else:
        flagged_basis = flagged_pays.groupby(group_keys, as_index=False).agg(
            _final_pay_date=("_pay_date", "min"),
            _flagged_final_pay_count=("_pay_date", "count"),
        )
        flagged_basis["_final_pay_basis"] = BASIS_FLAGGED

        flagged_basis = flagged_basis.merge(
            proxy_basis[group_keys + ["_post_termination_pay_count"]],
            on=group_keys,
            how="left",
        )

        remaining_proxy = proxy_basis.merge(
            flagged_basis[group_keys],
            on=group_keys,
            how="left",
            indicator=True,
        )
        remaining_proxy = remaining_proxy[remaining_proxy["_merge"] == "left_only"].drop(
            columns=["_merge"]
        )

        final_pay = pd.concat([flagged_basis, remaining_proxy], ignore_index=True)

    review = term.merge(
        final_pay,
        on=group_keys,
        how="left",
    )

    review = review[review["_final_pay_date"].notna()].copy()
    if review.empty:
        return []

    review["_days_diff"] = (review["_final_pay_date"] - review["_termination_date"]).dt.days

    cfg = rule.get("config", {}) or {}
    threshold = int(cfg.get("max_days_after_termination", DEFAULT_FINAL_PAY_DAYS_THRESHOLD))

    review_flagged = review[review["_days_diff"] > threshold].copy()
    if review_flagged.empty:
        return []

    text = rule.get("text", {})
    base_msg = text.get(
        "finding",
        "Final pay for one or more terminated employees was recorded later than the configured timing threshold.",
    )
    remediation = text.get(
        "remediation",
        "Confirm the final pay date for the affected employees and review termination processing timeliness. Where a delay was expected, record the reason so the timing can be explained if reviewed.",
    )
    severity = rule.get("severity", "HIGH")

    findings: List[Finding] = []

    for _, row in review_flagged.iterrows():
        emp_id = str(row["employee_id"]).strip()
        term_date = row["_termination_date"]
        final_pay_date = row["_final_pay_date"]
        days_diff = int(row["_days_diff"])
        basis = str(row["_final_pay_basis"])

        primary_keys = {
            "employee_id": emp_id,
            "termination_date": str(term_date.date()) if pd.notna(term_date) else None,
        }

        if basis == BASIS_FLAGGED:
            explanation = (
                "The pay event flagged as final was recorded more than the configured "
                "number of days after the termination date. This is a payroll timing "
                "anomaly for review, not a determination that any obligation was breached."
            )
        else:
            explanation = (
                "No pay event on or after termination was flagged as final, so the latest "
                "post-termination pay event was used as a proxy for final pay. The gap "
                "exceeds the configured threshold. Because the final pay event is not "
                "identifiable from the data supplied, confirm the actual final pay date "
                "before drawing any conclusion about timing."
            )

        evidence_obj = {
            "sources": ["terminations.csv", "pay_events.csv"],
            "primary_keys": primary_keys,
            "values": {
                "termination_date": str(term_date.date()) if pd.notna(term_date) else None,
                "derived_final_pay_date": str(final_pay_date.date()) if pd.notna(final_pay_date) else None,
                "days_after_termination": days_diff,
                "final_pay_basis": basis,
                "final_pay_flag_available": final_pay_flag_col is not None,
                "post_termination_pay_count": int(row["_post_termination_pay_count"])
                if pd.notna(row.get("_post_termination_pay_count"))
                else None,
                "flagged_final_pay_count": int(row["_flagged_final_pay_count"])
                if pd.notna(row.get("_flagged_final_pay_count"))
                else None,
            },
            "thresholds": {
                "max_days_after_termination": threshold,
            },
            "explanation": explanation,
        }

        findings.append(
            build_finding(
                rule,
                primary_keys=primary_keys,
                employee_id=emp_id,
                as_of_date=str(term_date.date()) if pd.notna(term_date) else None,
                severity=severity,
                message=base_msg,
                diff_units=float(days_diff),
                evidence=json.dumps(evidence_obj, ensure_ascii=False),
                next_action=remediation,
            )
        )

    return findings


def run_rule(rule: dict, datasets: Dict[str, pd.DataFrame]) -> List[Finding]:
    rule_id = rule.get("id")

    if rule_id == "RKEG-TERM-001":
        return _term_001_final_pay_outside_threshold(rule, datasets)

    return []