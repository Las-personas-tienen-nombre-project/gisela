"""Simulacion exploratoria independiente del motor GISELA.

No implementa el DSL de GISELA; simula el sistema de combate acordado
usando politicas explicitas y supuestos documentados en este archivo.

Uso: python simulador_dragon_workshop.py --runs 5000 --seed 20261103
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field

from simulador_models import (
    ALL,
    BASE,
    HEROES,
    MAIN,
    Attack,
    BasicAttack,
    Buff,
    Damage,
    FightConfig,
    seeded_rng,
)
from simulador_policies import PolicyMixin


@dataclass
class Combatant:
    name: str
    hpmax: int
    mpmax: int
    hp: int
    mp: int
    tpmax: int
    tp: int = 0
    turns: int = 0
    buffs: dict = field(default_factory=dict)
    paralyzed: bool = False
    knocked_down: bool = False
    protects: str | None = None
    shield: bool = False

    def active(self):
        return self.hp > 0 and not self.knocked_down

    def hp_pct(self):
        return self.hp / self.hpmax


class Fight(PolicyMixin):
    def __init__(self, rng, config=None):
        config = config or FightConfig()
        revised, shield_policy, knight_policy, trace = (
            config.revised,
            config.shield_policy,
            config.knight_policy,
            config.trace,
        )
        self.rng = rng
        self.revised = revised
        self.shield_policy = shield_policy
        self.knight_policy = knight_policy
        self.trace = trace
        self.log = []
        self.fighters = {}
        for name in ALL:
            b = BASE[name]
            if name == "dragon":
                hpmax = 500 + sum(self.d(20) for _ in range(3))
                mpmax = 80 + self.d(20)
                tpmax = 60
            else:
                hpmax = 150 + b["str"] + self.d(20)
                mpmax = 50 + b["int"] + self.d(10)
                tpmax = 50
            self.fighters[name] = Combatant(name, hpmax, mpmax, hpmax, mpmax, tpmax)
        scores = {
            x: BASE[x]["str"] + BASE[x]["awa"] + BASE[x]["for_"] + self.d(10)
            for x in ALL
        }
        self.order = sorted(
            ALL,
            key=lambda x: (
                -scores[x],
                -BASE[x]["awa"],
                -BASE[x]["str"],
                -BASE[x]["for_"],
                ALL.index(x),
            ),
        )
        self.round = 0
        self.phase = "onslaught"
        self.counts = Counter()
        self.damage_by = Counter()
        self.hit_count = Counter()
        self.ko_by = Counter()
        self.dragon_recovery_round = None
        self.deaths = []

    def d(self, n):
        return self.rng.randint(1, n)

    def note(self, msg):
        if self.trace:
            self.log.append(f"R{self.round} {msg}")

    def c(self, name):
        return self.fighters[name]

    def has(self, name, buff):
        return buff in self.c(name).buffs

    def stat(self, name, stat):
        val = BASE[name][stat]
        if self.has(name, "bless") and stat == MAIN[name]:
            val += 2
        if name == "dragon" and stat == "awa" and self.has("dragon", "agarraguirre"):
            val -= 2
        return val

    def apply_buff(self, name, effect: Buff):
        buff, turns, potency, source = (
            effect.buff,
            effect.turns,
            effect.potency,
            effect.source,
        )
        self.c(name).buffs[buff] = {
            "turns": turns,
            "applied": self.c(name).turns,
            "potency": potency,
            "source": source,
        }
        self.note(f"{name} obtiene {buff} (duracion {turns})")

    def begin_turn(self, name):
        p = self.c(name)
        p.turns += 1
        if name == "dragon" and self.has("dragon", "protegido"):
            p.buffs.pop("protegido")  # hasta comienzo del siguiente turno propio
            self.note("dragon pierde protegido")
        if p.paralyzed:
            p.paralyzed = False
            self.counts[name + ":turno_perdido"] += 1
            self.note(f"{name} pierde el turno por paralisis")
            self.end_turn(name)
            return False
        if name == "caballero" and p.protects:
            p.protects = None  # proteccion hasta siguiente turno del caballero
        if self.has(name, "regeneracion"):
            e = p.buffs["regeneracion"]
            if p.turns > e["applied"]:
                # INT del lanzador fijado en aplicacion
                amount = 5 + e["potency"] + self.d(10)
                self.heal(name, amount)
                self.counts["regeneracion_ticks"] += 1
        return True

    def end_turn(self, name):
        p = self.c(name)
        for buff, effect in list(p.buffs.items()):
            if buff == "protegido":
                continue
            if p.turns > effect["applied"]:
                effect["turns"] -= 1
                if effect["turns"] <= 0:
                    del p.buffs[buff]
                    self.note(f"{name}: expira {buff}")

    def heal(self, name, amount, revive=False):
        p = self.c(name)
        if not p.active() and not revive:
            return 0
        if revive:
            p.knocked_down = False
        before = p.hp
        p.hp = min(p.hpmax, p.hp + amount)
        self.note(f"{name} recupera {p.hp - before} HP (ahora {p.hp})")
        return p.hp - before

    def gain_tp(self, name, amount):
        p = self.c(name)
        p.tp = min(p.tpmax, p.tp + amount)

    def gain_mp(self, name, amount):
        p = self.c(name)
        p.mp = min(p.mpmax, p.mp + amount)

    def spend(self, name, cost=0, resource="mp"):
        p = self.c(name)
        if getattr(p, resource) < cost:
            return False
        setattr(p, resource, getattr(p, resource) - cost)
        return True

    def can_hit(self, att, defender, extra_hit=0):
        evade_base = (self.stat(defender, "str") + self.stat(defender, "awa")) // 2
        if defender in ("caballero", "enano"):
            evade_base += 2  # Dodge pasiva
        if defender == "dragon":
            evade_base -= 5  # Enorme
        if defender == "enano" and self.has("enano", "agresiva"):
            evade_base -= 2
        if att == "enano" and self.has("enano", "agresiva"):
            extra_hit += 2
        H = self.d(10) + self.stat(att, "awa") + extra_hit
        E = self.d(10) + evade_base
        return H > E

    def dmg_reduction(self, defender, kind):
        red = 0
        if defender == "dragon" and kind == "physical":
            red += 5  # Escamas
        if defender in ("mago", "sacerdotisa") and kind == "magic":
            red += 3  # Magic Redux
        if self.has(defender, "armadura_magica"):
            red += 3
        if self.has(defender, "protegido"):
            red += 5
        return red

    def apply_damage(self, damage: Damage):
        owner, target, raw, kind, skill, claw_special = (
            damage.owner,
            damage.target,
            damage.raw,
            damage.kind,
            damage.skill,
            damage.claw_special,
        )
        p = self.c(target)
        reduced = max(0, raw - self.dmg_reduction(target, kind))
        if reduced > 0:
            p.hp = max(0, p.hp - reduced)
            if owner == "dragon" and target in ("caballero", "enano"):
                self.gain_tp(target, 5)
            if target == "dragon":
                self.gain_tp("dragon", 5)
            self.damage_by[owner] += reduced
            self.note(
                f"{owner}:{skill} hace {reduced} {kind} a {target} ({p.hp}/{p.hpmax})"
            )
            if claw_special and self.d(20) == 1:
                p.hp = 0
                self.counts["zarpa_ko_critico"] += 1
                self.note(f"¡{target} cae por efecto especial de Zarpa!")
            if p.hp == 0:
                p.knocked_down = True
                self.ko_by[target] += 1
                self.note(f"{target} cae")
        return reduced

    def attack(self, attack: Attack):
        owner, skill, targets = attack.owner, attack.skill, attack.targets
        kind, raw, extra_hit, claw, paralyze = (
            attack.kind,
            attack.raw,
            attack.extra_hit,
            attack.claw,
            attack.paralyze,
        )
        self.counts[skill] += 1
        self.note(f"{owner} ejecuta {skill} contra {targets}")
        if owner == "dragon":
            self.phase = "onslaught"
            self.counts["dragon_attack_in_phase_" + str(self.phase)] += 1
            if self.c("sacerdotisa").shield:
                self.c("sacerdotisa").shield = False
                self.counts["group_shield_blocks"] += 1
                self.note("Groupal Shield bloquea la habilidad completa")
                return
        for target in targets:
            if not self.c(target).active():
                continue
            if not self.can_hit(owner, target, extra_hit):
                continue
            self.hit_count[skill] += 1
            final_target = target
            knight = self.c("caballero")
            intercepted = False
            if (
                owner == "dragon"
                and target in HEROES
                and knight.active()
                and knight.protects == target
            ):
                final_target = "caballero"
                knight.protects = None
                intercepted = True
            dealt = self.apply_damage(
                Damage(owner, final_target, raw, kind, skill, claw_special=claw)
            )
            if intercepted and dealt > 0:
                # Cambiar ganancia normal de TP del golpe por +10 de interceptacion.
                self.gain_tp("caballero", 5)
                self.counts["proteccion_intercepts"] += 1
                self.note("Proteccion intercepta el ataque")
            if paralyze and dealt > 0 and self.c(target).active():
                # status se aplica al destinatario final, despues de redirecciones
                if final_target != target:
                    continue
                if not self.c(target).paralyzed:
                    resist = (
                        self.d(10)
                        + self.stat(target, "str")
                        + self.stat(target, "for_")
                    )
                    if resist < 19:
                        self.c(target).paralyzed = True
                        self.counts["wingblast_paralysis"] += 1
                        self.note(f"{target}: paralizado por Wingblast")

    def basic_attack(self, who, attack=None):
        attack = attack or BasicAttack()
        skill, count, power, resource_cost = (
            attack.skill,
            attack.count,
            attack.power,
            attack.resource_cost,
        )
        self.c(who)
        if resource_cost and not self.spend(who, resource_cost, "tp"):
            return False
        if who == "caballero" and skill == "slash":
            self.gain_tp(who, 10)
        if who == "enano" and skill == "hachazo":
            self.gain_tp(who, 10)
        for i in range(count):
            if self.c("dragon").active():
                dmg = self.d(10) + 3 * self.stat(who, "str") + power
                if self.has(who, "grito"):
                    dmg += 3
                if self.has(who, "firesteel"):
                    dmg += 3
                self.attack(Attack(who, skill, ["dragon"], "physical", dmg))
        return True

    def cast_baston(self, who):
        if self.c("dragon").active():
            dmg = self.d(10) + 3 * self.stat(who, "str")
            self.attack(Attack(who, "bastonazo", ["dragon"], "physical", dmg))
        return True

    def magic_blast(self):
        p = self.c("mago")
        if p.mp < 11:
            return False
        x = min(40, p.mp - 1)
        if self.phase == "onslaught":
            x = min(x, 15)
        if x < 10:
            return False
        self.spend("mago", 1 + x, "mp")
        dmg = self.d(10) + self.stat("mago", "int") + x
        self.attack(
            Attack("mago", "magic_blast", ["dragon"], "magic", dmg, extra_hit=x // 10)
        )
        return True

    def result(self, max_rounds=30):
        for r in range(1, max_rounds + 1):
            self.round = r
            for who in self.order:
                if not self.c("dragon").active():
                    return self.outcome("grupo")
                if all(not self.c(h).active() for h in HEROES):
                    return self.outcome("dragon")
                if not self.c(who).active():
                    continue
                if not self.begin_turn(who):
                    continue
                actions = 3 if who in ("enano", "dragon") else 2
                # Atributo principal modificado por Bless en inicio del turno.
                score = self.stat(who, MAIN[who])
                actions = 3 if score >= 10 else (2 if score >= 7 else 1)
                for _ in range(actions):
                    if not self.c(who).active():
                        break
                    if not self.c("dragon").active():
                        break
                    if who == "dragon":
                        self.dragon_action()
                    elif who == "sacerdotisa":
                        self.priest_action()
                    elif who == "mago":
                        self.mage_action()
                    elif who == "enano":
                        self.dwarf_action()
                    else:
                        self.knight_action()
                self.end_turn(who)
        return self.outcome("limite")

    def outcome(self, result):
        return {
            "result": result,
            "round": self.round,
            "counts": dict(self.counts),
            "damage": dict(self.damage_by),
            "ko": dict(self.ko_by),
            "dragon_hp": self.c("dragon").hp,
            "survivors": sum(self.c(h).active() for h in HEROES),
            "hero_hp": {h: self.c(h).hp for h in HEROES},
            "first_recovery": self.dragon_recovery_round,
            "log": self.log,
            "order": self.order,
        }


def simulate(runs, seed, config):
    from simulador_reporting import summarize

    rng = seeded_rng(seed)
    results = []
    for _ in range(runs):
        sample = seeded_rng(rng.randrange(2**64))
        results.append(Fight(sample, config).result())
    return summarize(results, config)


def main():
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20261103)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    if args.trace:
        f = Fight(
            seeded_rng(args.seed), FightConfig(True, "anticipate", "defensive", True)
        )
        r = f.result()
        print("Resultado:", r["result"], "ronda", r["round"], "iniciativa", r["order"])
        print("\n".join(r["log"]))
        return
    for revised in (False, True):
        for shield_policy in ("phase", "anticipate"):
            for knight_policy in ("defensive", "aggressive"):
                print(
                    json.dumps(
                        simulate(
                            args.runs,
                            args.seed,
                            FightConfig(revised, shield_policy, knight_policy),
                        ),
                        ensure_ascii=False,
                    )
                )


if __name__ == "__main__":
    main()
