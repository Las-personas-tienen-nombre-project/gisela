#!/usr/bin/env python3
"""Recorridos de aceptación H4.6; consume exclusivamente Observe/Act."""
from __future__ import annotations
import argparse
import json
from functools import lru_cache
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'gisela/packages/h46_faro_de_niebla.package.json'

INTRO = ['escuchar_aviso', 'continue', 'continue']
FINALE = ['subir_cupula', 'emitir_senal', 'continue']
CLOSE = ['continue', 'continue', 'continue', 'continue']
ROUTES = {
    'completa': [*INTRO, 'colaborar', 'continue', 'entrar_archivo', 'leer_planos',
       'tomar_prisma', 'volver_muelle', 'entrar_taller', 'oido_uno', 'ayudar_elio',
       'continue', 'ayudar', 'continue', 'reparar_motor', 'continue', 'volver_muelle',
       *FINALE, 'emision_cuidadosa', *CLOSE],
    'sin_preparacion': [*INTRO, 'independiente', 'continue', *FINALE,
       'emision_urgente', *CLOSE],
    'parcial': [*INTRO, 'colaborar', 'continue', 'entrar_archivo', 'leer_planos',
       'volver_muelle', *FINALE, 'emision_cuidadosa', *CLOSE],
}


def advance(session, identifier):
    """Usa la oferta autorizada de la última proyección, no índices fijos."""
    view = session.observe()
    matches = [a for a in view['actions'] if a['id'] == identifier and a['enabled']]
    if len(matches) != 1:
        raise AssertionError(f'Acción {identifier!r} no ofertada: {view["actions"]}')
    request = {'session_id': view['session_id'], 'revision': view['revision'],
               'action_id': matches[0]['action_id']}
    reply = session.act(request)
    if reply['status'] != 'ok':
        raise AssertionError(f'Acción {identifier!r} falló: {reply}')
    return view


@lru_cache(maxsize=1)
def admitted_package():
    return admit_package_file(PACKAGE)

def run(route='completa', seed='1'*64, check_restores=False):
    """Recorre una variante y contrasta snapshots en puntos estables y pendientes."""
    admitted = admitted_package()
    session = new_session(admitted, seed=seed)
    records = []
    for identifier in ROUTES[route]:
        if check_restores:
            copy = restore_session(admitted, session.export())
            if copy.export() != session.export() or copy.observe() != session.observe():
                raise AssertionError('Guardado/restauración divergente')
        view = advance(session, identifier)
        records.append((view['status'], view['content']['kind'], identifier))
    if session.observe()['status'] != 'ended':
        raise AssertionError('El recorrido no terminó')
    return {'session': session, 'events': records, 'admitted': admitted}


def main():
    parser = argparse.ArgumentParser(description='Prueba E2/E3 de aventura en GLAUQUIR')
    parser.add_argument('--route', choices=sorted(ROUTES), default='completa')
    parser.add_argument('--seed', default='1'*64)
    parser.add_argument('--verify-restores', action='store_true')
    parser.add_argument('--save', type=Path)
    args = parser.parse_args()
    result = run(args.route, args.seed, args.verify_restores)
    session = result['session']
    snapshot = session.export()
    if args.save:
        args.save.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+'\n')
    facts = [item['fact'] for item in snapshot['history']['facts']]
    print(json.dumps({'route': args.route, 'ending': snapshot['ending'],
          'turns': snapshot['turn'], 'world_time': snapshot['world_time'],
          'facts': facts, 'steps': len(result['events'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
