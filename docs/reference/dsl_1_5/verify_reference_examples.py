import copy,json
from pathlib import Path
from gisela.contracts.admit_package import admit_package,admit_package_file,PackageRejected
from gisela.engine.runtime import new_session,restore_session
root=Path.cwd(); src=root/'gisela/packages/ejemplo_minimo.package.json'
p=json.loads(src.read_text()); a=admit_package_file(src)
log=[]
def check(name, condition, details=''):
    assert condition,name+': '+details
    log.append('PASS '+name+((': '+details) if details else ''))
for option, expected in [('abrir','adentro'),('seguir','afuera')]:
    s=new_session(a,seed='a'*64)
    for i in range(8):
        v=s.observe()
        if v['status']=='ended':break
        act=next((x for x in v['actions'] if x['id']==option),v['actions'][0]); r=s.act({'session_id':v['session_id'],'revision':v['revision'],'action_id':act['action_id']})
        check('action '+option+' step '+str(i),r['status']=='ok')
    check('ending '+option,s.export()['ending']==expected)
s=new_session(a,seed='b'*64)
v=s.observe(); before=s.export()
check('observe pure',s.observe()==v and s.export()==before)
wrong={'session_id':v['session_id'],'revision':v['revision'],'action_id':'not_offered'}
r=s.act(wrong)
check('unoffered action rejected without mutation',r['error']['code']=='INVALID_ACTION' and s.export()==before)
valid={'session_id':v['session_id'],'revision':v['revision'],'action_id':v['actions'][0]['action_id']}
stale=copy.deepcopy(valid);stale['revision']+=1;r=s.act(stale)
check('stale action rejected without mutation',r['error']['code']=='STALE_PROJECTION' and s.export()==before)
clone=restore_session(a,s.export());check('restore same observe',clone.observe()==s.observe())
check('same action after restore',s.act(valid)==clone.act(valid) and s.export()==clone.export())
first=new_session(a,seed='b'*64);second=new_session(a,seed='b'*64)
check('equal seed equal initial state',first.export()==second.export())
bad=copy.deepcopy(p);bad['manifest']['format_version']='1.6'
try:admit_package(bad)
except PackageRejected as exc:check('wrong format rejected',bool(exc.diagnostics),str(exc.diagnostics[0].code))
else:raise AssertionError('wrong format admitted')
bad=copy.deepcopy(p);bad['nodes'][0]['steps'][1]['options'][0]['next']['node']='missing_node'
try:admit_package(bad)
except PackageRejected as exc:check('dangling node rejected',bool(exc.diagnostics),str(exc.diagnostics[0].code))
else:raise AssertionError('dangling node admitted')
path=root/'docs/reference/dsl_1_5/EXECUTION_EVIDENCE.md'
path.write_text('# Verified reference examples\n\nSource package: `gisela/packages/ejemplo_minimo.package.json`. This is a complete executable JSON package. Run with `PYTHONPATH=. python docs/reference/dsl_1_5/verify_reference_examples.py` from the repository root. These examples are automated checks of the public package admission, session, Observe, Act and restore APIs. They are not proof of every DSL mechanism.\n\n'+ '\n'.join('- '+x for x in log)+'\n',encoding='utf8')
print('\n'.join(log))
