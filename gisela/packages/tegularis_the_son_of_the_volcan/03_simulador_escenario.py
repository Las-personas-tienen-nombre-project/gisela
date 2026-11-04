"""BANCO DE PRUEBAS (NO GISELA). Reproduce parcialmente el diseño de Tegularis.

Se utiliza para experimentar con el combate mientras los contratos productivos
necesarios todavía no forman parte de GISELA 0.1.21.
"""

from __future__ import annotations

import argparse
import statistics
from collections import Counter

from simulador_base import HEROES, Fight
from simulador_models import Attack, BasicAttack, Damage, ScenarioConfig, seeded_rng

NAMES = {
    "caballero": "Parnecio Esparcales",
    "enano": "Gillius Cabezadeencina",
    "sacerdotisa": "Clarisa de la Hojarasca",
    "mago": "Iosepus Knechti",
    "dragon": "Tegularis, el Hijo del Volcán",
}


class FightTegularis(Fight):
    def __init__(self, rng, config=None):
        config = config or ScenarioConfig()
        self.pride_active = False
        self.death_burst_fired = False
        self.interactive = config.interactive
        self.death_burst_enabled = config.death_burst
        super().__init__(rng, config)
        self.c("dragon").tp = 50

    def stat(self, name, stat):
        return super().stat(name, stat) + (
            1 if name == "dragon" and self.pride_active else 0
        )

    def dmg_reduction(self, defender, kind):
        return super().dmg_reduction(defender, kind) + (
            1 if defender == "dragon" and self.pride_active else 0
        )

    def attack(self, attack: Attack):
        owner, skill, targets = attack.owner, attack.skill, attack.targets
        kind, raw, extra_hit, claw, paralyze = (
            attack.kind,
            attack.raw,
            attack.extra_hit,
            attack.claw,
            attack.paralyze,
        )
        if owner == "dragon" and self.pride_active and raw is not None:
            raw += 5
        return super().attack(
            Attack(owner, skill, targets, kind, raw, extra_hit, claw, paralyze)
        )

    def apply_damage(self, damage: Damage):
        owner, target, raw, kind, skill, claw_special = (
            damage.owner,
            damage.target,
            damage.raw,
            damage.kind,
            damage.skill,
            damage.claw_special,
        )
        was_alive = self.c("dragon").active() if target == "dragon" else False
        dealt = super().apply_damage(
            Damage(owner, target, raw, kind, skill, claw_special)
        )
        if target == "dragon" and was_alive:
            d = self.c("dragon")
            if d.hp > 0 and d.hp_pct() <= 0.30 and not self.pride_active:
                self.pride_active = True
                self.counts["pride_of_the_volcan_son"] += 1
                self.note("Tegularis despierta Pride of the Volcan Son")
            if d.hp == 0 and self.death_burst_enabled and not self.death_burst_fired:
                self.resolve_final_burst()
        return dealt

    def resolve_final_burst(self):
        # Se marca antes de emitir consecuencias, para garantizar exact-once.
        self.death_burst_fired = True
        self.counts["ultima_llama"] += 1
        raw = 30 + self.stat("dragon", "int") + self.d(10)
        self.note(
            f"Tegularis: «Si vas a perder asegúrate de que no ganan por mucho» ({raw} daño bruto)"
        )
        if self.c("sacerdotisa").shield:
            self.c("sacerdotisa").shield = False
            self.counts["group_shield_blocks_final"] += 1
            self.note("Groupal Shield neutraliza toda la explosión")
            return
        for hero in HEROES:
            if not self.c(hero).active():
                continue
            final = hero
            knight = self.c("caballero")
            if hero != "caballero" and knight.active() and knight.protects == hero:
                knight.protects = None
                final = "caballero"
            super().apply_damage(Damage("dragon", final, raw, "magic", "ultima_llama"))

    def outcome(self, result):
        out = super().outcome(result)
        if self.c("dragon").hp == 0 and all(not self.c(h).active() for h in HEROES):
            out["result"] = "destruccion_mutua"
        out["pride_active"] = self.pride_active
        out["death_burst_fired"] = self.death_burst_fired
        return out

    def knight_action(self):
        if not self.interactive:
            return super().knight_action()
        knight = self.c("caballero")
        print(
            f"\nRonda {self.round} | Tegularis {self.c('dragon').hp}/{self.c('dragon').hpmax} HP"
        )
        for name in HEROES:
            c = self.c(name)
            print(
                f"  {NAMES[name]}: {c.hp}/{c.hpmax} HP; {c.mp}/{c.mpmax} MP; {c.tp}/{c.tpmax} TP"
            )
        print(
            "  1: Slash (+10 TP)  2: Double Slash (10 TP)  3: Blai (30 TP)  4: Protección  5: Pasar"
        )
        try:
            choice = input("Parnecio > ").strip()
        except EOFError:
            choice = "1"
        if choice == "2" and knight.tp >= 10:
            return self.basic_attack(
                "caballero", BasicAttack("double_slash", count=2, resource_cost=10)
            )
        if choice == "3" and knight.tp >= 30:
            return self.basic_attack(
                "caballero", BasicAttack("blai", power=8, resource_cost=30)
            )
        if choice == "4":
            allies = [h for h in ("sacerdotisa", "mago", "enano") if self.c(h).active()]
            if allies:
                target = min(allies, key=lambda h: self.c(h).hp_pct())
                knight.protects = target
                self.counts["proteccion"] += 1
                print("Parnecio protege a", NAMES[target])
                return
        if choice == "5":
            return
        self.basic_attack("caballero", BasicAttack("slash"))


def check():
    from test_simulador_escenario import test_scenario_self_check

    test_scenario_self_check()


def main():
    a = argparse.ArgumentParser()
    a.add_argument(
        "--play",
        action="store_true",
        help="Probar elecciones de Parnecio en el simulador independiente",
    )
    a.add_argument("--runs", type=int, default=250)
    a.add_argument("--seed", type=int, default=20261103)
    a.add_argument("--trace", action="store_true")
    a.add_argument("--test", action="store_true")
    args = a.parse_args()
    if args.test:
        return check()
    if args.play or args.trace:
        f = FightTegularis(
            seeded_rng(args.seed), ScenarioConfig(interactive=args.play, trace=True)
        )
        res = f.result()
        print("\nResultado:", res["result"], "ronda", res["round"])
        if args.trace:
            print("\n".join(res["log"]))
        else:
            print(
                "Daño total:",
                res["damage"],
                "Pride:",
                res["pride_active"],
                "Explosión:",
                res["death_burst_fired"],
            )
    else:
        generator = seeded_rng(args.seed)
        results = [
            FightTegularis(
                seeded_rng(generator.randrange(2**64)), ScenarioConfig()
            ).result()
            for _ in range(args.runs)
        ]
        r = Counter(x["result"] for x in results)
        print(
            "Combates:",
            args.runs,
            "| Resultado:",
            dict(r),
            "| Mediana rondas:",
            statistics.median(x["round"] for x in results),
        )
        print(
            "Pride:",
            sum(x["pride_active"] for x in results),
            "| Ultima llama:",
            sum(x["death_burst_fired"] for x in results),
        )


if __name__ == "__main__":
    main()
