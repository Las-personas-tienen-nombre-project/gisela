#!/usr/bin/env python3
"""Comprueba límites de tamaño en el código y la documentación mantenidos.

Los manuscritos y los archivos históricos no se modifican por esta política.
"""
from __future__ import annotations
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ('gisela', 'tools', 'renpy', 'docs', 'mary', 'narrative_conditions', 'traits', 'dice')
EXTENSIONS = {'.py', '.rpy', '.md', '.json', '.toml', '.txt'}
EXCLUDED = {'docs/narrative/reference/Blue_Forever.md'}
MAX_FILE_LINES = 500
MAX_FUNCTION_LINES = 30
MAX_PARAMETERS = 3


def maintained_files(root: Path):
    """Recorre material mantenido, pero no respaldos ni fuentes narrativas."""
    for name in FOLDERS:
        for path in (root / name).rglob('*'):
            relative = path.relative_to(root).as_posix()
            if path.is_file() and path.suffix in EXTENSIONS and relative not in EXCLUDED:
                if not any(part in {'.venv', '__pycache__', '.git'} for part in path.parts):
                    yield path


def function_lines(node: ast.AST) -> int:
    """Descuenta líneas ocupadas por la cadena de documentación inicial."""
    count = node.end_lineno - node.lineno + 1
    body = node.body
    if body and isinstance(body[0], ast.Expr):
        first = body[0].value
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            count -= body[0].end_lineno - body[0].lineno + 1
    return count


def function_parameters(node: ast.AST, *, method: bool = False) -> int:
    """Cuenta entradas explícitas; self y cls son receptores implícitos."""
    args = node.args
    positional = [*args.posonlyargs, *args.args]
    count = len(positional) + len(args.kwonlyargs)
    count += int(args.vararg is not None) + int(args.kwarg is not None)
    if method and positional and positional[0].arg in ('self', 'cls'):
        count -= 1
    return count


def problems(path: Path, root: Path) -> list[str]:
    """Devuelve infracciones con ubicación verificable."""
    relative = path.relative_to(root).as_posix()
    source = path.read_text(encoding='utf-8')
    count = len(source.splitlines())
    issues = []
    if count > MAX_FILE_LINES:
        issues.append(f'{relative}: {count} líneas, máximo {MAX_FILE_LINES}')
    if path.suffix == '.py':
        tree = ast.parse(source, filename=str(path))
        parents = {child: parent for parent in ast.walk(tree)
                   for child in ast.iter_child_nodes(parent)}
        functions = (node for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
        for node in functions:
            size = function_lines(node)
            if size > MAX_FUNCTION_LINES:
                issues.append(f'{relative}:{node.lineno}: {node.name}, {size} líneas, máximo {MAX_FUNCTION_LINES}')
            method = isinstance(parents.get(node), ast.ClassDef) and not any(
                isinstance(d, ast.Name) and d.id == 'staticmethod'
                for d in node.decorator_list)
            parameters = function_parameters(node, method=method)
            if parameters > MAX_PARAMETERS:
                issues.append(f'{relative}:{node.lineno}: {node.name}, {parameters} parámetros, máximo {MAX_PARAMETERS}')
    return issues


def check(root: Path = ROOT) -> list[str]:
    """Agrupa los incumplimientos sin modificar archivos."""
    return [issue for path in maintained_files(root) for issue in problems(path, root)]


def main() -> int:
    """Imprime el estado de la política estructural del proyecto."""
    issues = check()
    for issue in issues:
        print('ERROR:', issue)
    if not issues:
        print('OK: máximo 500 líneas por archivo, 30 por función y 3 parámetros explícitos')
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())
