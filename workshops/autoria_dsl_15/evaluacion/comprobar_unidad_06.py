"""Comprobaciones de admisión y propiedades para Unidad 6; no es material de autoría."""
from pathlib import Path
import json
from gisela.contracts.admit_package import PackageRejected, admit_package_file
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'workshops/autoria_dsl_15'
CANON=ROOT/'packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json'
base=json.loads(CANON.read_text())
def part(p,name):return next(x for x in p['actuation']['participants'] if x['character']==name)
def property(p,n):
 a=p['actuation']
 if n=='01_iniciativa':return a['initiative_die']
 if n=='02_umbrales':return a['thresholds'][0]['at']
 if n=='03_atributo':return part(p,'clarisa')['main_stat']
 if n=='04_candidatos':return tuple(c['skill_instance'] for c in part(p,'gillius')['candidates'])
 if n=='05_guarda':return part(p,'tegularis')['candidates'][0].get('when')
 raise ValueError(n)
for group in ('ejercicios','soluciones'):
 for f in sorted((W/group/'06_actuacion').glob('*.package.json')):
  n=f.stem.replace('.package','')
  if n=='06_referencia_invalida':
   try: admit_package_file(f)
   except PackageRejected:print('RECHAZO ESPERADO',n)
   else:raise AssertionError('Se admitió una referencia inexistente')
   continue
  admit_package_file(f)
  p=json.loads(f.read_text())
  if group=='ejercicios':assert property(p,n)!=property(base,n),(group,n)
  else:assert p==base,(group,n)
  print('ADMISIÓN',group,n)
print('UNIDAD 6: admisión y propiedades verificadas')
