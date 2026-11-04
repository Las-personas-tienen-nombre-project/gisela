"""Regresiones del simulador: explosión única y trayectorias deterministas."""

import hashlib
import importlib.util
import json
import random
from pathlib import Path

from simulador_base import HEROES, Fight
from simulador_models import Damage, FightConfig, ScenarioConfig

SPEC = importlib.util.spec_from_file_location(
    "tegularis_scenario", Path(__file__).with_name("03_simulador_escenario.py")
)
SCENARIO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCENARIO)
FightTegularis = SCENARIO.FightTegularis


def test_scenario_self_check():
    f = FightTegularis(random.Random(7), ScenarioConfig(trace=True))
    assert f.c("dragon").tp == 50
    assert f.stat("dragon", "str") == 15
    f.c("dragon").hp = round(f.c("dragon").hpmax * 0.30)
    f.apply_damage(Damage("caballero", "dragon", 1, "physical", "prueba"))
    assert f.pride_active and f.stat("dragon", "str") == 16
    for hero in HEROES:
        f.c(hero).hp = 1
    f.c("dragon").hp = 1
    f.apply_damage(Damage("caballero", "dragon", 50, "physical", "prueba"))
    assert f.death_burst_fired
    assert f.counts["ultima_llama"] == 1
    assert f.outcome("grupo")["result"] == "destruccion_mutua"
    f.apply_damage(Damage("caballero", "dragon", 50, "physical", "prueba"))
    assert f.counts["ultima_llama"] == 1
    g = FightTegularis(random.Random(11), ScenarioConfig())
    assert g.result()["result"] in ("grupo", "dragon", "limite", "destruccion_mutua")
    print(
        "OK: TP inicial, Pride, explosión exact-once, destrucción mutua y recorrido automático"
    )


def test_seeded_transcripts_and_rng_unchanged():
    records = []
    for seed in range(10):
        for revised in (False, True):
            for shield in ("phase", "anticipate"):
                for knight in ("defensive", "aggressive"):
                    rng = random.Random(seed)
                    fight = Fight(rng, FightConfig(revised, shield, knight, True))
                    records.append((fight.result(), rng.getstate()))
        for burst in (False, True):
            rng = random.Random(seed)
            fight = FightTegularis(rng, ScenarioConfig(trace=True, death_burst=burst))
            records.append((fight.result(), rng.getstate()))
    encoded = json.dumps(records, ensure_ascii=False, sort_keys=True).encode()
    # Fixture capturada antes del refactor: 100 recorridos, trazas completas y RNG final.
    assert (
        hashlib.sha256(encoded).hexdigest()
        == "d9dd325e07d57cbb9e6d75d0250f4b110401402e94128dc4672e69994b852380"
    )
