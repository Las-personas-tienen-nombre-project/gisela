"""Resumen estadístico de recorridos reproducibles del simulador."""

import statistics
from collections import Counter

from simulador_models import ALL, HEROES

ACTION_NAMES = (
    "firebreath",
    "wingblast",
    "coletazo",
    "zarpa",
    "dentellada",
    "preponderancia",
    "groupal_shield",
    "group_shield_blocks",
    "curacion",
    "fenix",
    "concentracion_sacerdotisa",
    "regeneracion",
    "regeneracion_ticks",
    "bless",
    "agarraguirre",
    "armadura_magica",
    "firesteel",
    "magic_blast",
    "concentracion_mago",
    "slash",
    "double_slash",
    "blai",
    "hachazo",
    "eviscerate",
    "stance_aggressive",
    "grito_de_guerra",
    "proteccion",
    "proteccion_intercepts",
    "wingblast_paralysis",
    "zarpa_ko_critico",
)


def summarize(results, config):
    runs = len(results)
    revised, shield_policy, knight_policy = (
        config.revised,
        config.shield_policy,
        config.knight_policy,
    )
    total = Counter(r["result"] for r in results)
    return {
        "escenario": ("nuevo" if revised else "anterior")
        + "/"
        + shield_policy
        + "/"
        + knight_policy,
        "n": runs,
        "victorias_grupo_pct": 100 * total["grupo"] / runs,
        "victorias_dragon_pct": 100 * total["dragon"] / runs,
        "limite_pct": 100 * total["limite"] / runs,
        "mediana_rondas": statistics.median(r["round"] for r in results),
        "media_rondas": statistics.mean(r["round"] for r in results),
        "media_supervivientes": statistics.mean(r["survivors"] for r in results),
        "recuperacion_ronda_media": statistics.mean(
            r["first_recovery"] for r in results if r["first_recovery"] is not None
        ),
        "media_por_combate": {
            key: round(statistics.mean(r["counts"].get(key, 0) for r in results), 3)
            for key in ACTION_NAMES
        },
        "KO_pct_por_heroe": {
            h: round(100 * sum(r["ko"].get(h, 0) > 0 for r in results) / runs, 2)
            for h in HEROES
        },
        "daño_medio_por_combate": {
            h: round(statistics.mean(r["damage"].get(h, 0) for r in results), 1)
            for h in ALL
        },
    }
