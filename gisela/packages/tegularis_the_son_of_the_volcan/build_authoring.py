"""Construcción de cartas y recursos declarativos; sin reglas del motor."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillPlay:
    effects: list
    requirements: dict | None = None
    outcomes: list | None = None


@dataclass(frozen=True)
class AttackDefinition:
    cid: str
    who: str
    target: str
    stat_name: str = "strength"
    extra: int = 0
    tp_gain: int = 0
    tp_cost: int = 0
    mp_cost: int = 0
    style: str = "physical"
    evade: int = 6
    extra_hit: int = 0


@dataclass(frozen=True)
class EffectDefinition:
    cid: str
    turns: int
    on_apply: list | None = None
    on_expire: list | None = None
    on_start: list | None = None


from build_expressions import (
    ResourceGain,
    active,
    add,
    cond_all,
    cost,
    damage,
    eq,
    evasion,
    gain,
    has_resource,
    inc,
    lit,
    maximum,
    message,
    mul,
    put,
    reduce_damage,
    roll,
    stat,
    sub,
    trait,
    var,
)


class CardBuilder:
    def __init__(self, package):
        self.people = ("parnecio", "gillius", "clarisa", "iosepus", "tegularis")
        self.package = package
        self.variables = {x["id"]: x for x in package["manifest"]["variables"]}
        self.cards = {c["id"]: c for c in package["cards"] if c["kind"] == "skill"}

    def define(self, key, value):
        if key not in self.variables:
            item = {"scope": "session", "id": key, "type": "integer", "initial": value}
            self.package["manifest"]["variables"].append(item)
            self.variables[key] = item
            self.package["initial_state"]["session_variables"][key] = value

    def equip(self, cid, play: SkillPlay):
        effects, requirements, outcomes = play.effects, play.requirements, play.outcomes
        card = self.cards[cid]
        card["play"]["effects"] = effects
        card["play"]["requires"] = requirements or {"constant": True}
        card["play"]["outcomes"] = outcomes or []
        card.pop("description", None)

    def hit_and_damage(self, attack: AttackDefinition):
        """Un intento con tiradas independientes y daño solo al acertar."""
        cid = attack.cid
        who = attack.who
        target = attack.target
        tp_gain = attack.tp_gain
        tp_cost = attack.tp_cost
        mp_cost = attack.mp_cost
        style = attack.style
        hk = "scratch_hit_" + who
        ek = "scratch_eva_" + who
        dk = "scratch_damage_" + who
        effects = []
        if tp_cost:
            effects.append(cost(who, "tp", tp_cost))
        if mp_cost:
            effects.append(cost(who, "mp", mp_cost))
        if tp_gain:
            effects.append(
                gain(
                    who,
                    "tp",
                    ResourceGain(lit(tp_gain), 50 if who != "tegularis" else 60),
                )
            )
        effects += self._attack_rolls(attack)
        hit = eq(var(hk), "gt", var(ek))
        # Mitigación computada después del acierto, no antes.
        effective = maximum(
            lit(0),
            sub(sub(var(dk), var("defense_" + target)), reduce_damage(target, style)),
        )
        outcomes = [
            {
                "when": hit,
                "effects": [
                    damage(target, effective),
                    message(
                        cid.upper() + " hizo {damage} puntos de daño a {target}.",
                        damage=effective,
                        target=lit(target),
                    ),
                ],
            },
            {
                "when": {"not": hit},
                "effects": [message(target + " esquivó " + cid.upper() + ".")],
            },
        ]
        reqs = [active(who), active(target)]
        if tp_cost:
            reqs.append(has_resource(who, "tp", tp_cost))
        if mp_cost:
            reqs.append(has_resource(who, "mp", mp_cost))
        self.equip(cid, SkillPlay(effects, cond_all(*reqs), outcomes))

    def effect_card(self, effect: EffectDefinition):
        cid = effect.cid
        turns = effect.turns
        on_apply = effect.on_apply
        on_expire = effect.on_expire
        on_start = effect.on_start
        item = {
            "id": cid,
            "kind": "effect",
            "title": {"text": cid},
            "stacking": "unique_per_target",
            "on_reapply": "refresh",
            "actuation_turns": turns,
        }
        if on_apply:
            item["on_apply"] = on_apply
        if on_expire:
            item["on_expire"] = on_expire
        if on_start:
            item["on_actor_turn_start"] = on_start
        self.package["cards"].append(item)

    def one_slash(self, i):
        h = f"double_hit_{i}"
        e = f"double_eva_{i}"
        d = f"double_dmg_{i}"
        for name in (h, e, d):
            self.define(name, 0)
        return [
            roll(h),
            inc(
                h,
                add(stat("parnecio", "awareness"), trait("parnecio", ["hit"], "actor")),
            ),
            roll(e),
            inc(e, evasion("tegularis")),
            roll(d),
            put(
                d,
                maximum(lit(0), add(var(d), mul(lit(3), stat("parnecio", "strength")))),
            ),
        ]

    def initial_resources(self):
        for w in self.people:
            # Los recursos aleatorios se decidirán en la integración de arranque.
            strength = {
                "parnecio": 8,
                "gillius": 10,
                "clarisa": 4,
                "iosepus": 4,
                "tegularis": 15,
            }[w]
            intelligence = {
                "parnecio": 4,
                "gillius": 4,
                "clarisa": 7,
                "iosepus": 9,
                "tegularis": 9,
            }[w]
            basehp = 500 if w == "tegularis" else 150 + strength
            basemp = 80 if w == "tegularis" else 50 + intelligence
            for k, v in [
                ("hp", basehp),
                ("max_hp", basehp),
                ("mp", basemp),
                ("max_mp", basemp),
                ("tp", 50 if w == "tegularis" else 0),
            ]:
                self.define(k + "_" + w, v)
            for k in ("hit", "eva", "damage"):
                self.define("scratch_" + k + "_" + w, 0)
            self.define("defense_" + w, 0)
            self.define("firesteel_" + w, 0)
            self.define("warcry_" + w, 0)

    def setup_resources(self):
        # Reglas iniciales autorales: dados al inicio del encuentro, no en cada ronda.
        setup = []
        for w in self.people:
            self.define("bonus_hp_" + w, 0)
            self.define("bonus_mp_" + w, 0)
            if w == "tegularis":
                for n in range(3):
                    self.define("bonus_dragon_" + str(n), 0)
                    setup.append(roll("bonus_dragon_" + str(n), 20))
                hp = add(lit(500), *(var("bonus_dragon_" + str(n)) for n in range(3)))
            else:
                setup.append(roll("bonus_hp_" + w, 20))
                hp = add(lit(150), stat(w, "strength"), var("bonus_hp_" + w))
            setup.extend(
                [
                    put("max_hp_" + w, hp),
                    put("hp_" + w, hp),
                    roll("bonus_mp_" + w, 20 if w == "tegularis" else 10),
                ]
            )
            mp = add(
                lit(80) if w == "tegularis" else add(lit(50), stat(w, "intelligence")),
                var("bonus_mp_" + w),
            )
            setup.extend([put("max_mp_" + w, mp), put("mp_" + w, mp)])
        self.package["actuation"]["setup"] = setup

    def double_slash(self):
        seq = [cost("parnecio", "tp", 10)] + self.one_slash(1) + self.one_slash(2)
        outs = []
        for i in (1, 2):
            success = eq(var(f"double_hit_{i}"), "gt", var(f"double_eva_{i}"))
            amount = maximum(
                lit(0),
                sub(
                    sub(var(f"double_dmg_{i}"), var("defense_tegularis")),
                    reduce_damage("tegularis", "physical"),
                ),
            )
            outs.append(
                {
                    "when": success,
                    "effects": [
                        damage("tegularis", amount),
                        message(
                            "DOUBLE SLASH impacto " + str(i) + ": {damage} puntos.",
                            damage=amount,
                        ),
                    ],
                }
            )
            outs.append(
                {
                    "when": {"not": success},
                    "effects": [
                        message(
                            "Tegularis esquivó DOUBLE SLASH impacto " + str(i) + "."
                        )
                    ],
                }
            )
        self.equip(
            "double_slash",
            SkillPlay(
                seq,
                cond_all(
                    active("parnecio"),
                    active("tegularis"),
                    has_resource("parnecio", "tp", 10),
                ),
                outs,
            ),
        )

    def _attack_rolls(self, attack):
        who = attack.who
        target = attack.target
        stat_name = attack.stat_name
        extra = attack.extra
        style = attack.style
        extra_hit = attack.extra_hit
        hk, ek, dk = "scratch_hit_" + who, "scratch_eva_" + who, "scratch_damage_" + who
        return [
            roll(hk),
            inc(
                hk,
                add(
                    stat(who, "awareness"), lit(extra_hit), trait(who, ["hit"], "actor")
                ),
            ),
            roll(ek),
            inc(ek, evasion(target)),
            roll(dk),
            put(
                dk,
                maximum(
                    lit(0),
                    add(
                        var(dk),
                        mul(lit(3), stat(who, stat_name)),
                        lit(extra),
                        var("firesteel_" + who) if style == "physical" else lit(0),
                        var("warcry_" + who) if style == "physical" else lit(0),
                        lit(0),
                    ),
                ),
            ),
        ]

    def groupal_shield(self, fire_out):
        # Una pantalla completa bloqueada consume una carga, no cada objetivo.
        self.equip(
            "groupal_shield",
            SkillPlay(
                [
                    cost("clarisa", "mp", 30),
                    put("group_shield", lit(1)),
                    message(
                        "GROUPAL SHIELD protegió al grupo del siguiente ataque de área."
                    ),
                ],
                cond_all(
                    active("clarisa"),
                    has_resource("clarisa", "mp", 30),
                    eq(var("group_shield"), "eq", lit(0)),
                ),
            ),
        )
        fire_out.insert(
            0,
            {
                "when": eq(var("group_shield"), "gt", lit(0)),
                "effects": [
                    put("group_shield", lit(0)),
                    message("GROUPAL SHIELD bloqueó FIREBREATH."),
                ],
            },
        )
        for item in fire_out[1:]:
            item["when"] = cond_all(eq(var("group_shield"), "eq", lit(0)), item["when"])
        # Actualiza la tarjeta compilada con las condiciones de escudo.
        self.cards["firebreath"]["play"]["outcomes"] = fire_out
