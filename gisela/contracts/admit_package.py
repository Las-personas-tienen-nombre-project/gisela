#!/usr/bin/env python3
"""Puerta única de admisión offline para paquetes autorales de GISELA.

NO inicia una sesión, NO interpreta el paquete y NO reemplaza a GISELA.
Para paquetes de archivo utiliza el lector JSON estricto; para datos ya
cargados, el llamante es responsable de rechazar claves duplicadas antes.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

try:
    from .semantic_validator import Diagnostic, Validator, load_json_strict
    from .canonical import canonical_json, package_digest, CanonicalError
except ImportError:  # Ejecución directa desde el directorio contracts
    from semantic_validator import Diagnostic, Validator, load_json_strict
    from canonical import canonical_json, package_digest, CanonicalError


@dataclass(frozen=True)
class AdmittedPackage:
    """Paquete admitido, conservado por copia; materialize() entrega otra copia."""
    _payload_json: str
    diagnostics: tuple[Diagnostic, ...]
    digest: str

    def materialize(self) -> dict:
        """Devuelve una copia independiente (NO referencia interna mutable)."""
        return json.loads(self._payload_json, parse_float=__import__("decimal").Decimal)


class PackageRejected(ValueError):
    """Rechazo de admisión con diagnósticos de contrato disponibles al llamante."""
    def __init__(self, diagnostics: tuple[Diagnostic, ...]):
        """Conserva diagnósticos y resume la cantidad de errores."""
        self.diagnostics = diagnostics
        errors = [d for d in diagnostics if d.severity == 'error']
        super().__init__(f'Paquete rechazado: {len(errors)} error(es) de contrato')


def admit_package(package: dict, *, reject_warnings: bool = False) -> AdmittedPackage:
    """Valida estructura + semántica. No admite paquetes con errores conocidos.

    Los warnings no son errores por defecto, pues incluyen riesgos narrativos
    y aspectos que solo podrá verificar el futuro ejecutor.
    """
    if not isinstance(package, dict):
        raise PackageRejected((Diagnostic('error','INVALID_PACKAGE','/',
                                          'La raíz del paquete debe ser un objeto JSON'),))
    checks = tuple(Validator().validate_package(package))
    if any(d.severity == 'error' or (reject_warnings and d.severity == 'warning') for d in checks):
        raise PackageRejected(checks)
    try:
        frozen_copy = canonical_json(package).decode("utf-8")
        digest = package_digest(package)
    except CanonicalError as exc:
        raise PackageRejected((Diagnostic("error", "CANONICAL_REJECTED", "/", str(exc)),)) from exc
    return AdmittedPackage(frozen_copy, checks, digest)


def admit_package_file(path: Path, *, reject_warnings: bool = False) -> AdmittedPackage:
    """Lee JSON estricto y admite estructura y semántica sin crear sesión.

    Propaga errores de lectura o sintaxis; los diagnósticos de contrato
    bloqueantes se entregan mediante PackageRejected.
    """
    return admit_package(load_json_strict(path), reject_warnings=reject_warnings)


def cli(argv: list[str] | None = None) -> int:
    """Expone la admisión offline; retorna 0, 1 o 2 según resultado."""
    parser = argparse.ArgumentParser(description='GISELA: puerta de admisión de paquetes autorales')
    parser.add_argument('package', type=Path)
    parser.add_argument('--json', action='store_true', help='Salida JSON apta para CI')
    parser.add_argument('--reject-warnings', action='store_true', help='Modo conservador: rechaza advertencias')
    args = parser.parse_args(argv)
    try:
        admitted = admit_package_file(args.package, reject_warnings=args.reject_warnings)
        diags, accepted, exit_code = admitted.diagnostics, True, 0
    except PackageRejected as exc:
        diags, accepted, exit_code = exc.diagnostics, False, 1
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        diags = (Diagnostic('error', 'INVALID_INPUT', '/', f'No se pudo leer el JSON: {exc}'),)
        accepted, exit_code = False, 2
    if args.json:
        print(json.dumps({'admitted':accepted,'package_digest':admitted.digest if accepted else None,'diagnostics':[asdict(d) for d in diags]},
                         ensure_ascii=False, indent=2))
    else:
        for d in diags: print(f'{d.severity.upper()} {d.code} {d.path}: {d.message}')
        print(('ADMITTED ' + admitted.digest) if accepted else 'REJECTED')
    return exit_code


if __name__ == '__main__':
    sys.exit(cli())
