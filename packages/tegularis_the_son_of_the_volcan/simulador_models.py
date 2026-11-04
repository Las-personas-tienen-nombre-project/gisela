"""Configuraciones y solicitudes del simulador independiente del DSL."""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class FightConfig:
    revised: bool = True
    shield_policy: str = "anticipate"
    knight_policy: str = "defensive"
    trace: bool = False


@dataclass(frozen=True)
class ScenarioConfig(FightConfig):
    interactive: bool = False
    death_burst: bool = True


@dataclass(frozen=True)
class Buff:
    buff: str
    turns: int = 3
    potency: int = 0
    source: str | None = None


@dataclass(frozen=True)
class Damage:
    owner: str
    target: str
    raw: int
    kind: str
    skill: str
    claw_special: bool = False


@dataclass(frozen=True)
class Attack:
    owner: str
    skill: str
    targets: list[str]
    kind: str = "physical"
    raw: int | None = None
    extra_hit: int = 0
    claw: bool = False
    paralyze: bool = False


@dataclass(frozen=True)
class BasicAttack:
    skill: str = "slash"
    count: int = 1
    power: int = 0
    resource_cost: int = 0


BASE = {
    "caballero": {"str": 8, "ope": 5, "for_": 6, "int": 4, "awa": 6},
    "enano": {"str": 10, "ope": 4, "for_": 5, "int": 4, "awa": 5},
    "sacerdotisa": {"str": 4, "ope": 7, "for_": 9, "int": 7, "awa": 7},
    "mago": {"str": 4, "ope": 5, "for_": 6, "int": 9, "awa": 8},
    "dragon": {"str": 15, "ope": 7, "for_": 5, "int": 9, "awa": 7},
}
HEROES = ("caballero", "enano", "sacerdotisa", "mago")
ALL = HEROES + ("dragon",)
MAIN = {
    "caballero": "str",
    "enano": "str",
    "sacerdotisa": "ope",
    "mago": "int",
    "dragon": "str",
}


def seeded_rng(seed):
    """Generador determinista de combate, sin credenciales ni tokens de seguridad."""
    return random.Random(seed)  # nosec B311 -- simulación reproducible, sin secretos.
