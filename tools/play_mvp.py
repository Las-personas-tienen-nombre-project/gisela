#!/usr/bin/env python3
"""Anfitrión de consola de la vertical mínima. Solo consume Observe/Act."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import load_json_strict
from gisela.engine.runtime import new_session, restore_session, EngineFailure
from tools.cli_commands import inspect, instructions

DEFAULT = ROOT / 'gisela' / 'packages' / 'mvp_casete.package.json'


from tools.cli_render import show as display
from tools.cli_interactive import TextClient
from tools.cli_render import confirmed


def _save(path: Path, snapshot: dict):
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _arguments(argv):
    """Lee las opciones de la consola, sin abrir sesiones."""
    parser = argparse.ArgumentParser(description='GLAUQUIR: cliente textual de GISELA')
    parser.add_argument('--package', type=Path, default=DEFAULT)
    parser.add_argument('--restore', type=Path, help='Guardar JSON de sesión existente')
    parser.add_argument('--save', type=Path, help='Exportar estado final de sesión')
    parser.add_argument('--auto', action='store_true', help='Recorrer la historia sin entrada interactiva')
    parser.add_argument('--developer', action='store_true', help='Permitir consultas diagnósticas del mundo')
    parser.add_argument('--choose', default='prestar',
                        help='Opción preferida para el recorrido automático')
    return parser.parse_args(argv)


def _choose_interactive(actions, session, args):
    """Traduce la interacción textual a un identificador autorizado."""
    return TextClient(session, args.developer).choose(session.observe())


def _choose_action(view, session, args):
    """Selecciona solo una acción visible en el último Observe."""
    actions = view['actions']
    if args.auto:
        candidates = [item for item in actions if item['enabled']]
        return next((item for item in candidates if item['id'] == args.choose), candidates[0])
    return _choose_interactive(actions, session, args)


def _run(session, args, admitted):
    """Consume Observe y Act, sin ejecutar reglas en el anfitrión."""
    for _ in range(256):
        view = session.observe()
        display(view)
        if not view['actions'] and (args.auto or view['status'] == 'ended'):
            return 0, session
        selected = _choose_action(view, session, args)
        if selected is None:
            return 0, session
        if selected.get('command') == 'load':
            from gisela.contracts.semantic_validator import load_json_strict
            from gisela.engine.runtime import restore_session
            try:
                session = restore_session(admitted, load_json_strict(Path(selected['path'])))
            except (EngineFailure, OSError, ValueError, KeyError) as exc:
                print('No se pudo cargar la sesión: ' + str(exc))
            continue
        previous = len(session.read_history())
        result = session.act({'session_id':view['session_id'],
                              'revision':view['revision'], 'action_id':selected['action_id']})
        if result['status'] == 'error':
            print(f'ERROR {result["error"]["code"]}: {result["error"]["message"]}', file=sys.stderr)
            return 1, session
        confirmed(session.read_history()[previous:])
    raise EngineFailure('BUDGET_EXCEEDED', 'La consola agotó el límite de pasos')


def main(argv=None):
    """Abre la sesión, ejecuta el anfitrión y guarda si se solicitó."""
    args = _arguments(argv)
    try:
        admitted = admit_package_file(args.package)
        session = (restore_session(admitted, load_json_strict(args.restore)) if args.restore
                   else new_session(admitted))
        status, session = _run(session, args, admitted)
        if args.save and status == 0:
            _save(args.save, session.export())
            print('Sesión guardada en ' + str(args.save))
        return status
    except (EngineFailure, OSError, ValueError, KeyError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
