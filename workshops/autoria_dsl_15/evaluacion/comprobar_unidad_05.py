"""Prueba dirigida para el material de habilidades; no forma parte de la autoría."""
from pathlib import Path
import json
from gisela.contracts.admit_package import PackageRejected, admit_package_file
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'workshops/autoria_dsl_15'
CANON=ROOT/'packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json'
base=json.loads(CANON.read_text())
def card(pkg,name):return next(c for c in pkg['cards'] if c['id']==name)
def extract(c,name):
    if name=='01_slash_tp':return card(c,'slash')['play']['effects'][0]['value']['math']['right']['math']['right']['literal']
    if name=='02_double_slash_costo':return card(c,'double_slash')['play']['effects'][0]['value']['literal']
    if name=='03_blai_requisito':return card(c,'blai')['play']['requires']['all'][2]['compare']['right']['literal']
    if name=='04_slash_acierto':return tuple(o['when'].get('compare',o['when'].get('not',{}).get('compare'))['op'] for o in card(c,'slash')['play']['outcomes'])
    if name=='05_blai_potencia':
        def find(obj):
            if isinstance(obj,dict):
                if obj=={'literal':8}: return 8
                for v in obj.values():
                    x=find(v)
                    if x is not None:return x
            elif isinstance(obj,list):
                for v in obj:
                    x=find(v)
                    if x is not None:return x
            return None
        return find(card(c,'blai')['play']['effects'][6]['value'])

for group in ('ejercicios','soluciones'):
 for p in sorted((W/group/'05_habilidades').glob('*.package.json')):
    if p.name.startswith('06_referencia_invalida'):
        try:admit_package_file(p)
        except PackageRejected:print('RECHAZO PREVISTO',p.name)
        else:raise AssertionError('No se rechazó referencia inexistente')
        continue
    admit_package_file(p)
    pkg=json.loads(p.read_text());name=p.name.split('.package.json')[0]
    if group=='soluciones':
        assert pkg==base,(group,name,'solución distinta del canónico')
    else:
        assert extract(pkg,name)!=extract(base,name),(group,name,'el punto de práctica no difiere')
    print('ADMISIÓN Y CONTROL',group,name)
print('UNIDAD 5: comprobaciones estructurales aprobadas')
