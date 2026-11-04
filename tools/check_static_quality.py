"""Evalúa los informes estructurados de Radon y Bandit sin editar el árbol."""

from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("gisela", "mary", "dice", "traits", "narrative_conditions")
BASELINE = ROOT / "tools/bandit_low_baseline.json"


def run_json(module: str, args: tuple[str, ...]) -> dict:
    """Ejecuta la herramienta del entorno actual y exige un informe íntegro."""
    command = (sys.executable, "-m", module, *args)
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode not in ((0, 1) if module == "bandit" else (0,)):
        raise ValueError(
            f"{module} falló (exit={result.returncode}): {result.stderr.strip()}"
        )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{module} no produjo JSON válido: {result.stderr.strip()}"
        ) from exc
    if not isinstance(report, dict) or not report:
        raise ValueError(f"{module} produjo un informe vacío o inválido")
    if module == "bandit" and (
        not isinstance(report.get("metrics"), dict)
        or "_totals" not in report["metrics"]
    ):
        raise ValueError("bandit produjo un informe incompleto")
    return report


def radon_issues(report: dict) -> tuple[list[str], int, float]:
    """Rechaza grados D-F y errores de lectura; calcula el promedio visible."""
    issues = []
    count = total = 0
    for path, blocks in report.items():
        if not isinstance(blocks, list):
            issues.append(f"{path}: análisis incompleto: {blocks}")
            continue
        for block in blocks:
            if not all(
                key in block for key in ("name", "lineno", "complexity", "rank")
            ):
                issues.append(f"{path}: bloque incompleto: {block}")
                continue
            count += 1
            total += block["complexity"]
            if block["rank"] in ("D", "E", "F"):
                name = (
                    f"{block.get('classname')}.{block['name']}"
                    if block.get("classname")
                    else block["name"]
                )
                issues.append(
                    f"{path}:{block['lineno']}: {name}, complejidad {block['complexity']}, grado {block['rank']}"
                )
    if count == 0:
        issues.append("Radon no analizó ningún bloque")
    return issues, count, total / count if count else 0.0


def test_path(path: Path) -> bool:
    """Clasifica solo directorios tests y archivos test_*.py como pruebas."""
    return (
        "tests" in path.parts or path.name.startswith("test_") and path.suffix == ".py"
    )


def bandit_issues(
    report: dict, baseline: list[dict], root: Path
) -> tuple[list[str], list[str]]:
    """Separa bloqueos de advertencias Low previamente revisadas."""
    if not isinstance(report.get("results"), list) or not isinstance(
        report.get("errors"), list
    ):
        return ["Bandit produjo un informe incompleto"], []
    blocking = [f"Bandit no pudo analizar: {error}" for error in report["errors"]]
    blocking.extend(
        f"Bandit omitió un archivo: {entry}"
        for entry in report.get("files_skipped", [])
    )
    allowed = collections.Counter(
        {
            (item["path"], item["rule"], item["source"]): item["count"]
            for item in baseline
        }
    )
    seen = collections.Counter()
    informational = []
    for issue in report["results"]:
        try:
            path = Path(issue["filename"]).resolve().relative_to(root.resolve())
            source = (
                (root / path)
                .read_text(encoding="utf-8")
                .splitlines()[issue["line_number"] - 1]
                .strip()
            )
            rule, severity = issue["test_id"], issue["issue_severity"]
        except (KeyError, ValueError, IndexError, OSError) as exc:
            blocking.append(f"Bandit produjo un hallazgo inválido: {exc}")
            continue
        label = f"{path}:{issue['line_number']}: {rule} {severity}"
        if not test_path(path) or severity != "LOW":
            blocking.append(label)
            continue
        key = (path.as_posix(), rule, source)
        seen[key] += 1
        if seen[key] > allowed[key]:
            blocking.append(f"{label}: Low de prueba nueva; requiere revisión")
        else:
            informational.append(f"{label}: {issue['issue_text']}")
    return blocking, informational


def check_radon() -> int:
    cc = run_json("radon", ("cc", *SOURCES, "-s", "-a", "-j"))
    mi = run_json("radon", ("mi", *SOURCES, "-s", "-j"))
    issues, count, average = radon_issues(cc)
    print(f"Radon CC: {count} bloques, promedio {average:.2f}")
    for path, value in mi.items():
        if not isinstance(value, dict) or "rank" not in value or "mi" not in value:
            issues.append(f"{path}: MI incompleto: {value}")
        elif value["rank"] == "C":
            print(f"MI informativo: {path}, C ({value['mi']:.2f})")
    for issue in issues:
        print(f"ERROR: {issue}")
    return int(bool(issues))


def source_files(root: Path) -> tuple[str, ...]:
    """Incluye fuentes mantenidas y excluye entornos y cachés anidados."""
    excluded = {".venv", ".git", "__pycache__"}
    return tuple(
        sorted(
            path.relative_to(root).as_posix()
            for folder in SOURCES
            for path in (root / folder).rglob("*.py")
            if not excluded.intersection(path.relative_to(root).parts)
        )
    )


def check_bandit() -> int:
    paths = source_files(ROOT)
    report = run_json("bandit", (*paths, "-f", "json", "-q"))
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    blocking, informational = bandit_issues(report, baseline, ROOT)
    scanned = {
        (ROOT / path).resolve().relative_to(ROOT.resolve()).as_posix()
        for path in report["metrics"]
        if path != "_totals"
    }
    blocking.extend(
        f"Bandit no analizó: {path}" for path in sorted(set(paths) - scanned)
    )
    for issue in informational:
        print(f"INFO: {issue}")
    for issue in blocking:
        print(f"ERROR: {issue}")
    print(
        f"Bandit: {len(informational)} Low conocidas en pruebas; {len(blocking)} bloqueantes"
    )
    return int(bool(blocking))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=("radon", "bandit"))
    args = parser.parse_args()
    try:
        return check_radon() if args.tool == "radon" else check_bandit()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
