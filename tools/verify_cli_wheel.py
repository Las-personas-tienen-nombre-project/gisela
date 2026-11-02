"""Verifica las CLI públicas desde una wheel instalada fuera del repositorio."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def run(
    command: list[str], cwd: Path, *, input_text: str = ""
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def expect(result: subprocess.CompletedProcess[str], code: int, marker: str) -> None:
    if result.returncode != code or marker not in result.stdout:
        raise AssertionError(
            f"Esperado exit={code} y {marker!r}; obtenido exit={result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def main() -> int:
    with TemporaryDirectory(prefix="gisela-wheel-cli-") as directory:
        temp = Path(directory)
        wheelhouse = temp / "wheels"
        wheelhouse.mkdir()
        build = run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir",
                str(wheelhouse),
                str(ROOT),
            ],
            temp,
        )
        if build.returncode:
            raise RuntimeError(build.stdout + build.stderr)
        (wheel,) = wheelhouse.glob("gisela_narrative_engine-*.whl")
        with ZipFile(wheel) as archive:
            names = archive.namelist()
            assert "gisela/packages/mvp_casete.package.json" in names
            assert "gisela/cli/glauquir.py" in names
            assert "gisela/cli/main.py" in names
            entries = archive.read(
                next(n for n in names if n.endswith("entry_points.txt"))
            ).decode()
            assert "glauquir = gisela.cli.glauquir:main" in entries
            assert "gisela = gisela.cli.main:main" in entries

        venv = temp / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        python = venv / "bin" / "python"
        installed = run([str(python), "-m", "pip", "install", str(wheel)], temp)
        if installed.returncode:
            raise RuntimeError(installed.stdout + installed.stderr)
        glauquir = str(venv / "bin" / "glauquir")
        gisela = str(venv / "bin" / "gisela")
        expect(run([glauquir, "--help"], temp), 0, "GLAUQUIR")
        expect(run([glauquir], temp), 0, "Alberto llega")

        package = temp / "historia.package.json"
        package.write_bytes(
            (ROOT / "gisela/packages/ejemplo_minimo.package.json").read_bytes()
        )
        expect(run([glauquir, "--package", str(package)], temp), 0, "Hay una puerta")
        expect(run([gisela, "validate", str(package)], temp), 0, "ADMITTED")
        package.write_text("{}", encoding="utf-8")
        expect(run([gisela, "validate", str(package)], temp), 1, "REJECTED")
        expect(
            run([gisela, "validate", str(temp / "missing.json"), "--json"], temp),
            2,
            '"INVALID_INPUT"',
        )
    print("Wheel CLI: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
