"""Tegularis-specific authoring helpers and compatibility imports.

Generic constructors are maintained in tools.authoring_expressions. Keep this
module for existing historical builder scripts and their output contracts.
"""

from dataclasses import dataclass
from pathlib import Path
import sys

# The historical builders also run directly, without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.authoring_expressions import (
    add, calc, cond_all, eq, inc, lit, maximum, message, minimum,
    mul, put, roll, stat, sub, trait, var,
)


@dataclass(frozen=True)
class ResourceGain:
    amount: dict
    maximum: int


def evasion(w):
    return add(
        calc("floor_divide", add(stat(w, "strength"), stat(w, "awareness")), lit(2)),
        trait(w, ["evasion"]),
    )


def reduce_damage(w, kind):
    return trait(w, [kind + "_damage_reduction"])


def active(k):
    return eq(var("hp_" + k), "gt", lit(0))


def has_resource(w, r, n):
    return eq(var(r + "_" + w), "gte", lit(n))


def cost(w, r, n):
    return inc(r + "_" + w, lit(-n))


def gain(w, r, change):
    n, maxn = change.amount, change.maximum
    return put(r + "_" + w, minimum(lit(maxn), add(var(r + "_" + w), n)))


def heal(w, amount):
    return put("hp_" + w, minimum(var("max_hp_" + w), add(var("hp_" + w), amount)))


def damage(w, amount):
    return put("hp_" + w, maximum(lit(0), sub(var("hp_" + w), amount)))
