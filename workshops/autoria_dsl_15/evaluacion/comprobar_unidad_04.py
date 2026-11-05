"""Comprobaciones reproducibles de contribuciones TRAITS para la Unidad 4.
Herramienta de evaluación, NO parte de la autoría del alumno.
Ejecutar desde la raíz: python -m workshops.autoria_dsl_15.evaluacion.comprobar_unidad_04
"""
from __future__ import annotations
import json
from pathlib import Path
from traits import compile_catalog, evaluate
from gisela.contracts.admit_package import PackageRejected, admit_package_file

ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'workshops/autoria_dsl_15'

def load(group,name):
    return json.loads((W/group/'04_rasgos'/f'{name}.package.json').read_text(encoding='utf8'))

def calculate(package,character,role,tags,slots=('bonus',)):
    assigned=next(c['traits'] for c in package['cards'] if c['id']==character)
    request={'schema_version':'traits.evaluation.v1','participants':[{'entity':character,'kind':'character','role':role,'traits':assigned}], 'tags':tags,'slots':list(slots)}
    return evaluate(compile_catalog(package['traits']),request)

def check(name,character,role,tags,expected,slot='bonus'):
    pkg=load('soluciones',name)
    result=calculate(pkg,character,role,tags,(slot,))
    value=result['totals'].get(slot,0)
    assert value==expected,(name,character,role,tags,value,expected)
    print('OK',name,character,role,tags,'total',value)

for group in ('ejercicios','soluciones'):
    for p in sorted((W/group/'04_rasgos').glob('*.json')):
        if p.name.startswith('06_rasgo_inexistente'):
            try: admit_package_file(p)
            except PackageRejected: print('OK rechazo deliberado',p.name)
            else: raise AssertionError('Se admitió un rasgo inexistente')
        else:
            admit_package_file(p)
            print('OK admisión',group,p.name)

check('01_dodge','parnecio','defender',['evasion'],2)
check('01_dodge','parnecio','actor',['evasion'],0)
check('01_dodge','parnecio','defender',['hit'],0)
check('02_penalizacion','gillius','defender',['evasion'],0) # dodge +2, paso torpe -2
check('02_penalizacion','gillius','defender',['hit'],0)
check('03_precision','parnecio','actor',['hit'],1)
check('03_precision','parnecio','defender',['hit'],0)
check('04_escamas','tegularis','defender',['physical_damage_reduction'],5)
check('04_escamas','tegularis','defender',['magic_damage_reduction'],0)
# pride_redux no está asignado de inicio: comprobar declaración con evaluación aislada
pkg=load('soluciones','05_pride_redux')
for tag in ('damage_reduction','physical_damage_reduction','magic_damage_reduction'):
    p=json.loads(json.dumps(pkg));next(c for c in p['cards'] if c['id']=='tegularis')['traits']=['pride_redux']
    result=calculate(p,'tegularis','defender',[tag]); assert result['totals']=={'bonus':1},result
    print('OK pride_redux definido para',tag)
check('05_pride_redux','tegularis','defender',['damage_reduction'],0)
print('UNIDAD 4: comprobaciones terminadas')
