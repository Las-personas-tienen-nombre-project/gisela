"""Herramientas públicas de autoría de GISELA."""

from __future__ import annotations

import argparse

from gisela.contracts.admit_package import cli as validate_cli


def main(argv: list[str] | None = None) -> int:
    """Despacha los comandos de autoría instalados."""
    parser = argparse.ArgumentParser(
        prog="gisela", description="Herramientas de autoría de GISELA"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validar un paquete narrativo")
    validate.add_argument("package")
    validate.add_argument(
        "--json", action="store_true", help="Emitir diagnósticos JSON"
    )
    validate.add_argument(
        "--reject-warnings", action="store_true", help="Rechazar advertencias"
    )
    args = parser.parse_args(argv)
    if args.command == "validate":
        forwarded = [args.package]
        if args.json:
            forwarded.append("--json")
        if args.reject_warnings:
            forwarded.append("--reject-warnings")
        return validate_cli(forwarded)
    parser.error("Comando desconocido")
