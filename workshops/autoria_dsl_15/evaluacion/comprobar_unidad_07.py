"""Evaluación de Unidad 7; código del instructor, no DSL autoral."""
from pathlib import Path
import json
from gisela.contracts.admit_package import admit_package_file
ROOT = Path(__file__).resolve().parents[3]
W = ROOT / 'workshops/autoria_dsl_15'
CANON = ROOT / 'packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json'
base = json.loads(CANON.read_text())
def card(p,id): return next(x for x in p['cards'] if x['id']==id)
def policy(p,id): return next(x for x in p['actuation']['event_policies'] if x['id']==id)
def prop(p,id):
    if id=='01_firebreath_area':return card(p,'firebreath')['play']['effects'][0]['value']['literal']
    if id=='02_paralisis':return card(p,'ef_paralizado_parnecio')['actuation_turns']
    if id=='03_regeneracion':return card(p,'ef_regen_parnecio')['actuation_turns']
    if id=='04_pride':return policy(p,'pride_of_the_volcan_son')['when']['all'][1]['compare']['right']['math']['right']['literal']
    if id=='05_ultima_llama':return policy(p,'ultima_llama')['effects'][1]['sides']
    if id=='06_desenlaces':return [x['id'] for x in p['actuation']['outcome_policies']]
    raise ValueError(id)
assert len(base['actuation']['outcome_policies'])==3
assert prop(base,'04_pride')==3
assert card(base,'ef_pride_volcan')['granted_traits']==['pride_redux']
assert policy(base,'ultima_llama')['phase']=='after_action'
assert policy(base,'ultima_llama')['effects'][0]['target']['var']['key']=='burst_shield_snapshot'
for group in ('ejercicios','soluciones'):
    for f in sorted((W/group/'07_tegularis').glob('*.package.json')):
        id=f.name.removesuffix('.package.json')
        if id=='07_error_efecto':
            try:admit_package_file(f)
            except Exception: print('RECHAZO ESPERADO',id)
            else:raise AssertionError('Se admitió una habilidad inexistente')
            continue
        admit_package_file(f)
        obj=json.loads(f.read_text())
        if group=='ejercicios':assert prop(obj,id)!=prop(base,id),(group,id)
        else:assert obj==base,(group,id)
        print('ADMISIÓN Y PROPIEDAD',group,id)
print('UNIDAD 7: comprobaciones estructurales satisfactorias; ramas de ejecución no certificadas')
