"""Verificación de admisión y equivalencia lógica, para instructor; no es DSL."""
import copy, json
from pathlib import Path
from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'workshops/autoria_dsl_15'
CANON=ROOT/'packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json'
canonical=json.loads(CANON.read_text())
LOGIC_KEYS=('revision','world_revision','turn','status','world_time','world','narrative','history','rng','actuation','cursor')
def logic(session):
 state=session.export()
 return {k:state[k] for k in LOGIC_KEYS}
def request(observation):
 available=[a for a in observation['actions'] if a['enabled']]
 if not available:return None
 return {'session_id':observation['session_id'],'revision':observation['revision'],'action_id':available[0]['action_id']}
filenames=sorted((W/'ejercicios/08_presentacion').glob('*.package.json'))
valid=[f for f in filenames if not f.name.startswith('08_')]
assert len(valid)==7
for f in valid:
 obj=json.loads(f.read_text());assert all(obj[k]==canonical[k] for k in canonical if k!='presentation'),f
 assert obj['presentation']!=canonical['presentation']
 admit_package_file(f)
 solution=W/'soluciones/08_presentacion'/f.name
 assert json.loads(solution.read_text())==canonical
 admit_package_file(solution)
 print('ADMISIÓN + LÓGICA INTACTA + SOLUCIÓN CANÓNICA:',f.name)
try:admit_package_file(filenames[-1])
except Exception:print('RECHAZO ESPERADO:',filenames[-1].name)
else:raise AssertionError('Plantilla con campo privado admitida')
packages=[admit_package_file(CANON)]+[admit_package_file(f) for f in valid]
for seed in ('0'*64,'f'*64):
 sessions=[new_session(p,seed=seed) for p in packages]
 for step in range(3):
  observations=[s.observe() for s in sessions]
  states=[logic(s) for s in sessions]
  assert states.count(states[0])==len(states),('divergencia',seed,step)
  assert all(o['actuation']==observations[0]['actuation'] for o in observations)
  actions=[request(o) for o in observations]
  assert all(a==actions[0] for a in actions)
  if step==1:
   sessions=[restore_session(p,json.loads(json.dumps(s.export()))) for p,s in zip(packages,sessions)]
   assert all(logic(s)==states[0] for s in sessions)
  if actions[0] is None:break
  for s in sessions:
   response=s.act(copy.deepcopy(actions[0]));assert response['status']=='ok',response
 print('REPLAY / RESTAURACIÓN / ESTADO LÓGICO IDÉNTICO:',seed, 'pasos:',step+1)
print('UNIDAD 8: verificaciones completadas; no certifica todas las ramas del combate')
