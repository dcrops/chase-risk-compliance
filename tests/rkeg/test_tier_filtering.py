"""Tier gating for RKEG rule selection.

The retired ``rkeg.engine.run_rkeg_engine`` took an ``enabled_tiers`` argument.
Tier selection now lives in ``rkeg.run.select_rules_by_tier``, which
``rkeg.run.main`` calls, so these tests target that function directly and use
the real rule configuration rather than a hand-built rule list.
"""

from src.rkeg.run import PRODUCTION_TIERS, select_rules_by_tier

TIER_2_RULE_ID = "RKEG-SUP-003"


def _ids(rules):
    return {str(r.get("id", "")).strip() for r in rules}


def test_the_reference_rule_is_still_tier_2(rkeg_rule):
    assert int(rkeg_rule(TIER_2_RULE_ID)["tier"]) == 2


def test_tier_2_rule_not_selected_when_only_tier_1_enabled(rkeg_rules):
    selected = select_rules_by_tier(rkeg_rules, tiers={1})

    assert TIER_2_RULE_ID not in _ids(selected)
    assert all(int(r.get("tier", 1)) == 1 for r in selected)


def test_tier_2_rule_selected_when_tier_2_enabled(rkeg_rules):
    selected = select_rules_by_tier(rkeg_rules, tiers={2})

    assert TIER_2_RULE_ID in _ids(selected)
    assert all(int(r.get("tier", 1)) == 2 for r in selected)


def test_production_selection_covers_tiers_one_and_two(rkeg_rules):
    selected = select_rules_by_tier(rkeg_rules)

    assert PRODUCTION_TIERS == frozenset({1, 2})
    assert TIER_2_RULE_ID in _ids(selected)
    assert _ids(selected) == _ids(select_rules_by_tier(rkeg_rules, tiers={1})) | _ids(
        select_rules_by_tier(rkeg_rules, tiers={2})
    )


def test_rules_without_a_tier_default_to_tier_1():
    rules = [{"id": "RKEG-TEST-001"}]

    assert select_rules_by_tier(rules, tiers={1}) == rules
    assert select_rules_by_tier(rules, tiers={2}) == []


def test_higher_tiers_are_excluded_from_production_runs(rkeg_rules):
    higher = [r for r in rkeg_rules if int(r.get("tier", 1)) > 2]
    selected_ids = _ids(select_rules_by_tier(rkeg_rules))

    assert _ids(higher).isdisjoint(selected_ids)
