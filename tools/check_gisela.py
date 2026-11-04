"""Verificador autónomo del repositorio GISELA, independiente de demos."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARIES = ("mary/tests", "dice/tests", "traits/tests", "narrative_conditions/tests")
CORE = (
    "gisela/contracts",
    "gisela/engine/tests",
    "gisela/packages/tegularis_the_son_of_the_volcan",
)
STATIC_SOURCES = ("gisela", "mary", "dice", "traits", "narrative_conditions", "tools")
STATIC_CHECKS = (
    (
        "Ruff — análisis estático",
        (sys.executable, "-m", "ruff", "check", *STATIC_SOURCES),
    ),
    (
        "Ruff — formato",
        (sys.executable, "-m", "ruff", "format", "--check", *STATIC_SOURCES),
    ),
    (
        "Radon — complejidad y mantenibilidad",
        (sys.executable, "tools/check_static_quality.py", "radon"),
    ),
    ("Bandit — seguridad", (sys.executable, "tools/check_static_quality.py", "bandit")),
)
CHECKS = (
    ("Calidad estructural", ("tools/check_quality.py",)),
    ("Enlaces documentales", ("tools/check_doc_links.py",)),
    ("Invariantes E0", ("tools/verify_e0_invariants.py",)),
    ("Invariantes E1", ("tools/verify_e1_invariants.py",)),
    ("Invariantes E2", ("tools/verify_e2_invariants.py",)),
    ("Invariantes E3", ("tools/verify_e3_invariants.py",)),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="Incluye recorridos narrativos completos con restauración",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Límite de segundos por comprobación (600)",
    )
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout debe ser positivo")
    commands = [
        (
            "Pruebas del motor, contratos y bibliotecas",
            (sys.executable, "-m", "pytest", "-q", *CORE, *LIBRARIES),
        ),
        (
            "Pruebas de herramientas",
            (
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tools/test_quality.py",
                "tools/test_doc_links.py",
                "tools/test_static_quality.py",
                "tools/test_tegularis_campaign.py",
            ),
        ),
    ]
    commands.extend(STATIC_CHECKS)
    commands.extend((label, (sys.executable, *argv)) for label, argv in CHECKS)
    if args.full:
        for script, routes in (
            ("h46_walkthrough.py", ("completa", "parcial", "sin_preparacion")),
            ("h46b_walkthrough.py", ("casete", "solo", "radio")),
        ):
            for route in routes:
                commands.append(
                    (
                        f"{script}: {route}",
                        (
                            sys.executable,
                            f"tools/{script}",
                            "--route",
                            route,
                            "--verify-restores",
                        ),
                    )
                )
    return run_checks(commands, args.timeout)


def run_checks(commands, timeout: int) -> int:
    """Ejecuta todas las comprobaciones y resume los fallos."""
    failures = []
    for label, cmd in commands:
        print(f"\n=== {label} ===", flush=True)
        start = time.perf_counter()
        try:
            code = subprocess.run(
                cmd, cwd=ROOT, timeout=timeout, check=False
            ).returncode
        except subprocess.TimeoutExpired:
            code = 124
        print(
            f"RESULTADO: {label}: exit={code}, segundos={time.perf_counter() - start:.2f}",
            flush=True,
        )
        if code:
            failures.append(label)
    print(
        f"\nGISELA: {len(commands) - len(failures)}/{len(commands)} comprobaciones satisfactorias.",
        flush=True,
    )
    for label in failures:
        print(f"FALLÓ: {label}", flush=True)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
