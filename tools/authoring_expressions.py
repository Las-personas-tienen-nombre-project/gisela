"""Pure constructors for authoring-time GISELA JSON expressions.

No runtime dependencies, I/O, evaluation or package-specific rules. These
functions only build dictionaries; package admission remains authoritative.
"""

import copy


def lit(x):
    return {"literal": copy.deepcopy(x)}


def var(x):
    return {"var": {"scope": "session", "key": x}}


def stat(w, x):
    return {"stat": {"character": w, "name": x, "component": "effective"}}


def trait(w, tags, role="defender"):
    return {
        "trait_total": {
            "participants": [{"entity": w, "role": role}],
            "tags": copy.deepcopy(tags),
            "slot": "bonus",
        }
    }


def calc(op, a, b):
    return {"math": {"op": op, "left": copy.deepcopy(a), "right": copy.deepcopy(b)}}


def add(*xs):
    if not xs:
        raise ValueError("At least one operand is required")
    result = copy.deepcopy(xs[0])
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
    return {"op": "set", "target": var(key), "value": copy.deepcopy(v)}


def inc(key, v):
    return {"op": "add", "target": var(key), "value": copy.deepcopy(v)}


def roll(key, n=10):
    return {"op": "roll", "sides": n, "store": var(key)}


def message(template, **kwargs):
    return {"op": "emit_message", "template": template, "values": copy.deepcopy(kwargs)}


def eq(a, op, b):
    return {"compare": {"left": copy.deepcopy(a), "op": op, "right": copy.deepcopy(b)}}


def cond_all(*v):
    return {"all": copy.deepcopy(list(v))}
