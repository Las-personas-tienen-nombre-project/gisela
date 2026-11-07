"""Pure authoring constructors remain stable across combat/noncombat content."""

import copy
import json

from packages.tegularis_the_son_of_the_volcan import build_expressions as legacy
from tools import authoring_expressions as expr


def test_legacy_helpers_keep_exact_structure():
    assert legacy.lit(4) == expr.lit(4)
    assert legacy.eq(legacy.var("time"), "gte", legacy.lit(20)) == expr.eq(
        expr.var("time"), "gte", expr.lit(20)
    )
    assert legacy.cost("parnecio", "tp", 20) == expr.inc("tp_parnecio", expr.lit(-20))
    assert legacy.damage("parnecio", expr.lit(3))["op"] == "set"


def test_noncombat_story_condition_and_event_without_tied_names():
    condition = expr.cond_all(
        expr.eq(expr.var("minute"), "gte", expr.lit(60)),
        expr.eq(expr.var("met_gisela"), "eq", expr.lit(True)),
    )
    effect = expr.put("heard_cassette", expr.lit(True))
    assert condition == {
        "all": [
            {
                "compare": {
                    "left": {"var": {"scope": "session", "key": "minute"}},
                    "op": "gte",
                    "right": {"literal": 60},
                }
            },
            {
                "compare": {
                    "left": {"var": {"scope": "session", "key": "met_gisela"}},
                    "op": "eq",
                    "right": {"literal": True},
                }
            },
        ]
    }
    assert effect["target"] == expr.var("heard_cassette")
    assert json.loads(json.dumps([condition, effect])) == [condition, effect]


def test_inputs_can_be_composed_without_mutating_previous_expression():
    baseline = expr.var("score")
    original = copy.deepcopy(baseline)
    combined = expr.add(baseline, expr.lit(1))
    combined["math"]["left"]["var"]["key"] = "other"
    assert baseline == original
