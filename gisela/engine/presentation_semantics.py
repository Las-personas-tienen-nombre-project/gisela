"""Safe, pure formatting of confirmed public causal events."""

from __future__ import annotations

from gisela.contracts.presentation_templates_validation import FIELDS, ROLES

LABELS = {
    "damage": "Daño",
    "healing": "Curación",
    "buff": "Beneficio",
    "debuff": "Perjuicio",
    "neutral": "Acontecimiento",
}


def clean(value) -> str:
    """Remove control characters (including ANSI ESC) from display-only text."""
    return "".join(char if char.isprintable() else " " for char in str(value))


def apply(events: list[dict], formats: list[dict]) -> None:
    """Decorate copied public records, never modifying history or semantics."""
    for event in events:
        for rule in formats:
            if rule["kind"] != event.get("kind"):
                continue
            if (
                "variable" in rule
                and event.get("detail", {}).get("variable") != rule["variable"]
            ):
                continue
            _decorate(event, rule)
            break


def _decorate(event: dict, rule: dict) -> None:
    role = rule.get("role", "neutral")
    if role not in ROLES:
        return
    event["semantic_role"] = role
    if "template" not in rule:
        return
    fields = FIELDS.get(event.get("kind"), frozenset())
    detail = event.get("detail", {})
    from string import Formatter

    names = [field for _, field, _, _ in Formatter().parse(rule["template"]) if field]
    if any(name not in fields for name in names):
        return
    if (
        any(name not in detail for name in names)
        and rule.get("missing", "omit") == "omit"
    ):
        return
    values = {name: clean(detail.get(name, "—"))[:160] for name in names}
    event["display_text"] = clean(rule["template"].format_map(values))[:1000]
