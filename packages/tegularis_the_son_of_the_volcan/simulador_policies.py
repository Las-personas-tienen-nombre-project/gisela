"""Políticas ordenadas del simulador, ajenas a las reglas del motor."""

import math

from simulador_models import HEROES, Attack, BasicAttack, Buff


class PolicyMixin:
    def priest_action(self):
        p = self.c("sacerdotisa")
        alive = [h for h in HEROES if self.c(h).active()]
        wounded = sorted(alive, key=lambda h: self.c(h).hp_pct())
        down = [h for h in HEROES if not self.c(h).active()]

        if self._priest_emergency(wounded, down):
            return
        if self._priest_shield(alive):
            return
        if self._priest_bless(alive, down):
            return
        if self._priest_regenerate(wounded):
            return
        # 8. curacion
        if (
            wounded
            and self.c(wounded[0]).hp_pct() < 0.85
            and self._priest_cure(wounded[0])
        ):
            return
        if p.mp <= p.mpmax - 30:
            self.gain_mp("sacerdotisa", 30)
            self.counts["concentracion_sacerdotisa"] += 1
            return
        self.cast_baston("sacerdotisa")

    def mage_action(self):
        p = self.c("mago")
        if not self.has("dragon", "agarraguirre") and p.mp >= 30:
            p.mp -= 30
            self.apply_buff("dragon", Buff("agarraguirre", turns=2, source="mago"))
            self.counts["agarraguirre"] += 1
            return
        if self._mage_support():
            return
        if self.dragon_recovery_round is not None and p.mp >= 40 and self.magic_blast():
            return
        if p.mp < p.mpmax - 25:
            self.gain_mp("mago", 30)
            self.counts["concentracion_mago"] += 1
            return
        if p.mp >= 30 and self.phase == "onslaught" and self.magic_blast():
            return
        self.cast_baston("mago")

    def dwarf_action(self):
        p = self.c("enano")
        if not self.has("enano", "agresiva"):
            self.apply_buff("enano", Buff("agresiva", turns=999))
            self.counts["stance_aggressive"] += 1
            return
        if not self.has("enano", "grito") and p.tp >= 10:
            p.tp -= 10
            self.apply_buff("enano", Buff("grito", turns=3))
            self.counts["grito_de_guerra"] += 1
            return
        if p.tp >= 30:
            self.basic_attack(
                "enano", BasicAttack("eviscerate", power=8, resource_cost=30)
            )
            return
        self.basic_attack("enano", BasicAttack("hachazo"))

    def knight_action(self):
        p = self.c("caballero")
        priest = self.c("sacerdotisa")
        if (
            self.knight_policy == "defensive"
            and self.phase == "onslaught"
            and priest.active()
            and priest.hp_pct() < 0.80
            and not p.protects
            and p.active()
        ):
            p.protects = "sacerdotisa"
            self.counts["proteccion"] += 1
            return
        if self.knight_policy == "aggressive":
            if p.tp >= 10:
                self.basic_attack(
                    "caballero", BasicAttack("double_slash", count=2, resource_cost=10)
                )
                return
        else:
            if p.tp >= 30:
                self.basic_attack(
                    "caballero", BasicAttack("blai", power=8, resource_cost=30)
                )
                return
            if p.tp >= 10:
                self.basic_attack(
                    "caballero", BasicAttack("double_slash", count=2, resource_cost=10)
                )
                return
        self.basic_attack("caballero", BasicAttack("slash"))

    def dragon_action(self):
        p = self.c("dragon")
        alive = [h for h in HEROES if self.c(h).active()]
        if not alive:
            return
        # Amenaza a la sacerdotisa primero, luego al mago; si no, al mas herido.
        target = min(
            alive,
            key=lambda h: (
                self.c(h).hp,
                {"sacerdotisa": 0, "mago": 1, "caballero": 2, "enano": 3}[h],
            ),
        )
        # Si hay TP y puede eliminar a un objetivo, selecciona Zarpa.
        if p.tp >= 20 and self.c(target).hp <= 65 and len(alive) >= 2:
            p.tp -= 20
            dmg = (
                self.d(10)
                + 3 * self.stat("dragon", "str")
                + (15 if self.revised else 0)
            )
            self.attack(
                Attack("dragon", "zarpa", [target], "physical", dmg, claw=self.revised)
            )
            return
        if self._dragon_interrupt(alive):
            return
        # Opta por ataques de area; Firebreath hace +15 en la revision.
        if p.mp >= 50 and len(alive) >= 2:
            p.mp -= 50
            dmg = (25 if self.revised else 10) + self.stat("dragon", "int") + self.d(10)
            self.attack(Attack("dragon", "firebreath", alive, "magic", dmg))
            return
        if p.tp >= 20 and len(alive) >= 2:
            p.tp -= 20
            dmg = 3 * self.stat("dragon", "str") + self.d(10)
            self.attack(Attack("dragon", "coletazo", alive, "physical", dmg))
            return
        if p.tp >= 20:
            # Zarpa superior a dentellada sin un efecto nuevo para esta ultima.
            p.tp -= 20
            dmg = (
                self.d(10)
                + 3 * self.stat("dragon", "str")
                + (15 if self.revised else 0)
            )
            self.attack(
                Attack("dragon", "zarpa", [target], "physical", dmg, claw=self.revised)
            )
            return
        # Si necesita tiempo, Wingblast tiene preferencia situacional durante Onslaught
        # pero compartir 50 MP y menos dano que Firebreath lo hace minoritario.
        # Recuperacion lenta con Protegido hasta el proximo turno propio.
        self.gain_mp("dragon", 8)
        self.gain_tp("dragon", 8)
        self.apply_buff("dragon", Buff("protegido", turns=1))
        self.phase = "recovery"
        self.counts["preponderancia"] += 1
        if self.dragon_recovery_round is None:
            self.dragon_recovery_round = self.round
        self.note("dragon usa Preponderancia: +8 MP +8 TP y protegido")

    def _priest_cure(self, h):
        if not self.spend("sacerdotisa", 20, "mp"):
            return False
        self.counts["curacion"] += 1
        amount = 20 + self.stat("sacerdotisa", "int") + self.d(10)
        self.heal(h, amount)
        return True

    def _priest_emergency(self, wounded, down):
        p = self.c("sacerdotisa")
        # 1. autoproteccion, si muy herida
        if p.hp_pct() < 0.50 and self._priest_cure("sacerdotisa"):
            return True
        # 2. aliados activos <=25%
        if (
            wounded
            and self.c(wounded[0]).hp_pct() <= 0.25
            and self._priest_cure(wounded[0])
        ):
            return True
        # 3. caidos
        if down and self.spend("sacerdotisa", 50, "mp"):
            target = min(
                down,
                key=lambda h: ("caballero", "enano", "mago", "sacerdotisa").index(h),
            )
            amount = math.ceil(self.c(target).hpmax / 2)
            self.heal(target, amount, revive=True)
            self.counts["fenix"] += 1
            return True
        return False

    def _priest_shield(self, alive):
        p = self.c("sacerdotisa")
        # 4. proteccion area: dos politicas de simulacion
        d = self.c("dragon")
        threat = d.mp >= 42 or d.tp >= 12
        shouldshield = (
            self.phase == "onslaught"
            if self.shield_policy == "phase"
            else (self.phase == "onslaught" or threat)
        )
        if shouldshield and not p.shield and p.mp >= 30:
            p.mp -= 30
            p.shield = True
            self.counts["groupal_shield"] += 1
            self.note("sacerdotisa aplica Groupal Shield")
            return True
        # 5. proteccion de aliados por el mismo shield, si amenaza fuerte
        if (
            any(self.c(h).hp_pct() < 0.55 for h in alive)
            and threat
            and not p.shield
            and p.mp >= 30
        ):
            p.mp -= 30
            p.shield = True
            self.counts["groupal_shield"] += 1
            return True
        return False

    def _priest_bless(self, alive, down):
        p = self.c("sacerdotisa")
        # 6. bless si todos > 60% durante recuperacion
        if (
            self.dragon_recovery_round is not None
            and alive
            and all(self.c(h).hp_pct() > 0.60 for h in alive)
            and not down
            and p.mp >= 10
        ):
            for h in ("enano", "caballero", "mago", "sacerdotisa"):
                if not self.has(h, "bless"):
                    p.mp -= 10
                    self.apply_buff(h, Buff("bless", turns=3, source="sacerdotisa"))
                    self.counts["bless"] += 1
                    return True
        return False

    def _priest_regenerate(self, wounded):
        p = self.c("sacerdotisa")
        # 7. regeneracion si alguien herido y no lo tiene
        for h in wounded:
            if (
                self.c(h).hp_pct() < 0.80
                and not self.has(h, "regeneracion")
                and p.mp >= 30
            ):
                p.mp -= 30
                self.apply_buff(
                    h,
                    Buff(
                        "regeneracion",
                        turns=3,
                        potency=self.stat("sacerdotisa", "int"),
                        source="sacerdotisa",
                    ),
                )
                self.counts["regeneracion"] += 1
                return True
        return False

    def _mage_support(self):
        p = self.c("mago")
        # Elige defensas prioritarias durante Onslaught
        if self.dragon_recovery_round is None and p.mp >= 30:
            for h in ("sacerdotisa", "mago"):
                if self.c(h).active() and not self.has(h, "armadura_magica"):
                    p.mp -= 30
                    self.apply_buff(h, Buff("armadura_magica", turns=2, source="mago"))
                    self.counts["armadura_magica"] += 1
                    return True
        if self.dragon_recovery_round is not None and p.mp >= 30:
            for h in ("enano", "caballero"):
                if (
                    self.c(h).active()
                    and not self.has(h, "firesteel")
                    and self.counts["firesteel_" + h] == 0
                ):
                    p.mp -= 30
                    self.apply_buff(h, Buff("firesteel", turns=2, source="mago"))
                    self.counts["firesteel"] += 1
                    self.counts["firesteel_" + h] += 1
                    return True
        return False

    def _dragon_interrupt(self, alive):
        p = self.c("dragon")
        # Una primera Wingblast intenta interrumpir a los lanzadores.
        # Luego Firebreath busca el mayor daño grupal. Politica del autor, NO regla GISELA.
        if (
            p.mp >= 50
            and len(alive) >= 2
            and self.counts["wingblast"] == 0
            and self.round <= 2
            and self.c("mago").active()
            and self.c("sacerdotisa").active()
            and not self.c("mago").paralyzed
            and not self.c("sacerdotisa").paralyzed
            and not self.c("sacerdotisa").shield
        ):
            p.mp -= 50
            dmg = 10 + self.stat("dragon", "str") + self.d(10)
            self.attack(
                Attack("dragon", "wingblast", alive, "magic", dmg, paralyze=True)
            )
            return True
        return False
