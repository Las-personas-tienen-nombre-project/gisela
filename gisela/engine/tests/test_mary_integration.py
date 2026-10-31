"""MARY participa de Observe/Act sin convertirse en autoridad de la sesión."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from gisela.contracts.admit_package import admit_package, admit_package_file, PackageRejected
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.errors import EngineFailure
from gisela.contracts.semantic_validator import Validator

FILE = Path(__file__).resolve().parents[2] / 'packages' / 'h45_cli.package.json'


def fixture():
    """Añade un objetivo oculto y una misión visible a la demo técnica."""
    package = admit_package_file(FILE).materialize()
    package['manifest']['facts'].append('meta_prestamo')
    package['mary'] = {'objectives':[
        {'id':'prestar', 'mode':'milestone', 'visibility':'hidden',
         'criterion':{'kind':'condition','when':{'has_fact':'alberto_presto_casete'}},
         'yield':{'fact':'meta_prestamo'}}], 'missions':[
        {'id':'encargo', 'title':'Préstamo del casete', 'visibility':'public',
         'objectives':['prestar'], 'completion':'all'}]}
    return package


def action(session, label):
    """Actúa únicamente mediante identificador publicado por Observe."""
    view=session.observe()
    selected=next(a for a in view['actions'] if a['label']==label)
    return session.act({'session_id':view['session_id'], 'revision':view['revision'],
                        'action_id':selected['action_id']})


class MaryGisela(unittest.TestCase):
    def test_admit_and_show_mission_without_hidden_objective(self):
        session=new_session(admit_package(fixture()))
        view=session.observe()
        self.assertEqual(view['quests'][0]['status'], 'active')
        self.assertNotIn('prestar', json.dumps(view['quests']))
        self.assertTrue(Validator().check_schema('observe', view))

    def test_scene_action_commits_progress_and_yield(self):
        session=new_session(admit_package(fixture()))
        result=action(session,'Entregar el casete')
        self.assertEqual(result['status'],'ok')
        facts=[entry['fact'] for entry in session.export()['history']['facts']]
        self.assertEqual(facts.count('meta_prestamo'),1)
        self.assertEqual(session.observe()['quests'][0]['status'],'completed')

    def test_rejected_action_does_not_change_mary(self):
        session=new_session(admit_package(fixture()))
        before=session.export()
        result=session.act({'session_id':'mvp_session', 'revision':0,
                            'action_id':'interact_999_999'})
        self.assertEqual(result['status'],'error')
        self.assertEqual(session.export(),before)

    def test_save_restore_does_not_duplicate_yield(self):
        admitted=admit_package(fixture());session=new_session(admitted)
        self.assertEqual(action(session,'Entregar el casete')['status'],'ok')
        saved=copy.deepcopy(session.export())
        restored=restore_session(admitted,saved)
        self.assertEqual(restored.export(),saved)
        self.assertEqual(len([x for x in saved['history']['facts']
                              if x['fact']=='meta_prestamo']),1)

    def test_missing_progress_rejected_on_restore(self):
        admitted=admit_package(fixture());session=new_session(admitted)
        saved=session.export();saved.pop('mary')
        with self.assertRaises(EngineFailure):restore_session(admitted,saved)

    def test_foreign_progress_rejected_on_restore(self):
        admitted=admit_package(fixture());session=new_session(admitted)
        saved=session.export();saved['mary']['objectives']['falso']=True
        with self.assertRaises(EngineFailure):restore_session(admitted,saved)

    def test_unknown_yield_rejected_before_start(self):
        data=fixture();data['mary']['objectives'][0]['yield']['fact']='no_declarado'
        with self.assertRaises(PackageRejected):admit_package(data)

    def test_unknown_condition_fact_rejected(self):
        package=fixture()
        package['mary']['objectives'][0]['criterion']['when']['has_fact']='inexistente'
        with self.assertRaises(PackageRejected):admit_package(package)

    def test_unknown_value_reference_rejected(self):
        package=fixture()
        package['mary']['objectives'][0]['criterion'] = {'kind':'condition',
          'when':{'compare':{'left':{'value':'session.no_declarada'},
                            'op':'eq','right':{'literal':True}}}}
        with self.assertRaises(PackageRejected):admit_package(package)

    def test_reaction_failure_rolls_back_mary_and_transfer(self):
        package=fixture()
        package['rules'].append({'id':'reaccion_fallida',
            'trigger':{'on':'fact_recorded','fact':'meta_prestamo'},
            'effects':[{'op':'transfer','object':'casete_01',
                        'from':'alberto','to':'gisela'}]})
        session=new_session(admit_package(package))
        before=session.export()
        result=action(session,'Entregar el casete')
        self.assertEqual(result['status'],'error')
        self.assertEqual(session.export(),before)

    def test_restored_future_action_determinism(self):
        admitted=admit_package(fixture())
        session=new_session(admitted)
        restored=restore_session(admitted,session.export())
        self.assertEqual(action(session,'Entregar el casete')['status'],'ok')
        self.assertEqual(action(restored,'Entregar el casete')['status'],'ok')
        self.assertEqual(session.export(),restored.export())

    def test_old_packages_unchanged(self):
        session=new_session(admit_package_file(FILE))
        self.assertNotIn('mary', session.export())
        self.assertNotIn('quests',session.observe())

    def test_pending_does_not_leak_incomplete_progress(self):
        session=new_session(admit_package(fixture()))
        before=session.export()
        self.assertNotIn('meta_prestamo', [x['fact'] for x in before['history']['facts']])
        self.assertEqual(before['mary']['objectives']['prestar'],False)


if __name__ == '__main__':
    unittest.main()
