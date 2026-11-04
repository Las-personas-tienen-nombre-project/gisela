"""Constructores puros de expresiones del paquete autoral Tegularis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceGain:
    amount: dict
    maximum: int


def lit(x):
    return {"literal": x}


def var(x):
    return {"var": {"scope": "session", "key": x}}


def stat(w, x):
    return {"stat": {"character": w, "name": x, "component": "effective"}}


def trait(w, tags, role="defender"):
    return {
        "trait_total": {
            "participants": [{"entity": w, "role": role}],
            "tags": tags,
            "slot": "bonus",
        }
    }


def evasion(w):
    return add(
        calc("floor_divide", add(stat(w, "strength"), stat(w, "awareness")), lit(2)),
        trait(w, ["evasion"]),
    )


def reduce_damage(w, kind):
    return trait(w, [kind + "_damage_reduction"])


def calc(op, a, b):
    return {"math": {"op": op, "left": a, "right": b}}


def add(*xs):
    result = xs[0]
    for x in xs[1:]:
        result = calc("add", result, x)
    return result


def sub(a, b):
    return calc("subtract", a, b)


def mul(a, b):
    return calc("multiply", a, b)


def minimum(a, b):
    return calc("min", a, b)


def maximum(a, b):
    return calc("max", a, b)


def put(key, v):
    return {"op": "set", "target": var(key), "value": v}


def inc(key, v):
    return {"op": "add", "target": var(key), "value": v}


def roll(key, n=10):
    return {"op": "roll", "sides": n, "store": var(key)}


def message(template, **kwargs):
    return {"op": "emit_message", "template": template, "values": kwargs}


def eq(a, op, b):
    return {"compare": {"left": a, "op": op, "right": b}}


def cond_all(*v):
    return {"all": list(v)}


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
