"""Read-only drift verification of supported GISELA authoring outputs.

Checks canonical v0.7.8 in isolation and all presentation/workshop variants.
No write mode; repairs use the individual generators.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEGULARIS = ROOT / "packages" / "tegularis_the_son_of_the_volcan"


def check_canonical():
    sources = (
        "build_v078.py",
        "build_expressions.py",
        "build_json.py",
        "09_cierre_autoral_v077.package.json",
        "v078_public_view.json",
    )
    with tempfile.TemporaryDirectory(prefix="gisela-authoring-") as directory:
        dest = Path(directory) / "packages" / "tegularis_the_son_of_the_volcan"
        dest.mkdir(parents=True)
        tools = Path(directory) / "tools"
        tools.mkdir()
        shutil.copy2(ROOT / "tools" / "authoring_expressions.py", tools)
        for name in sources:
            shutil.copy2(TEGULARIS / name, dest)
        subprocess.run(
            [sys.executable, str(dest / "build_v078.py")],
            cwd=dest,
            check=True,
            capture_output=True,
            text=True,
        )
        expected = (TEGULARIS / "10_balance_v078.package.json").read_bytes()
        actual = (dest / "10_balance_v078.package.json").read_bytes()
        if actual != expected:
            raise ValueError("Canonical package 10 differs from generated output")


def check_narrative_mvp():
    """Compare authored narrative nodes/reaction with the published MVP."""
    import json

    from tools.build_mvp_casete_authoring import compile_package

    path = ROOT / "gisela" / "packages" / "mvp_casete.package.json"
    canonical = json.loads(path.read_text(encoding="utf-8"))
    if compile_package(canonical) != canonical:
        raise ValueError("Narrative MVP differs from authored output")


def check_independent_narrative():
    """Ensure the noncombat example is built independently and remains current."""
    from tools.build_night_shift_authoring import OUTPUT, rendered

    if not OUTPUT.is_file() or OUTPUT.read_bytes() != rendered():
        raise ValueError("Independent narrative package differs from authored output")


def check_all():
    # Import late so that the tool still works when invoked from another cwd.
    sys.path.insert(0, str(ROOT))
    from docs.history.workshops.autoria_dsl_15.evaluacion.build_canonical_copies import (
        compile_copies,
    )
    from packages.tegularis_the_son_of_the_volcan.build_presentations import (
        compile_variants,
    )

    check_canonical()
    check_narrative_mvp()
    check_independent_narrative()
    names = compile_variants(check=True)
    count = compile_copies()
    return len(names), count


if __name__ == "__main__":
    variants, copies = check_all()
    print(
        f"OK: canonical package 10, {variants} presentations, {copies} workshop copies"
    )
