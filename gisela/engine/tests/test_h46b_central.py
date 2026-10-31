"""H4.6b: regresiones de la adaptación sin lógica específica en el engine."""
from __future__ import annotations
import json
import unittest
from functools import lru_cache
from gisela.engine.runtime import new_session, restore_session
from tools.h46_walkthrough import advance
from tools.h46b_walkthrough import admitted, play, take, settle, SEED


def fresh():
    return new_session(admitted(), seed=SEED)


def facts(s):
    return [entry['fact'] for entry in s.export()['history']['facts']]


@lru_cache(maxsize=8)
def saved(route, seed=SEED):
    """Solo snapshots terminales de lectura, nunca estados mutables de partida."""
    return play(route, seed).export()


def snapfacts(snapshot):
    return [entry['fact'] for entry in snapshot['history']['facts']]


class TestCentralClasificadora(unittest.TestCase):
    def test_admision_y_cuatro_espacios(self):
        pkg = admitted().materialize()
        self.assertEqual(pkg['manifest']['format_version'], '1.5')
        self.assertEqual({x['id'] for x in pkg['scenes']},
                         {'porteria', 'primer_piso', 'ascensor', 'puesto_b'})
        s=fresh()
        self.assertEqual((s.observe()['status'],s.observe()['scene']),('exploring','porteria'))

    def test_tres_finales_reales(self):
        for route, ending in [('casete','casete_en_la_pieza'),('solo','escalera_azul'),
                              ('radio','reporte_sin_novedad')]:
            with self.subTest(route=route):
                self.assertEqual(saved(route)['ending'], ending)

    def test_casete_cambia_propietario_y_epilogo(self):
        sent = saved('casete')
        solo = saved('solo')
        self.assertEqual(next(o for o in sent['world']['objects'] if o['id']=='casete_copia')['owner'],'gisela')
        self.assertEqual(next(o for o in solo['world']['objects'] if o['id']=='casete_copia')['owner'],'alberto')
        self.assertIn('casete_entregado',[x['fact'] for x in sent['history']['facts']])
        self.assertNotIn('casete_entregado',[x['fact'] for x in solo['history']['facts']])

    def test_autonomia_sin_puntaje_romantico(self):
        p = admitted().materialize()
        self.assertFalse(p['manifest']['relationship_fields'])
        self.assertNotIn('amor',json.dumps(p['manifest']))
        self.assertIn('amabilidad_observada',snapfacts(saved('casete')))
        self.assertEqual(snapfacts(saved('casete')).count('amabilidad_observada'),1)

    def test_horario_social_y_cierre(self):
        s=fresh(); take(s,'tomar_turno');take(s,'ponerse_a_trabajar')
        for _ in range(4):take(s,'esperar_hora')
        self.assertEqual(s.export()['world_time'],'1998-07-24T23:00:00-04:00')
        actions={x['id']:x for x in s.observe()['actions']}
        self.assertFalse(actions['esperar_hora']['enabled'])
        self.assertFalse(actions['preguntar_araya']['enabled'])
        self.assertTrue(actions['cerrar_turno']['enabled'])
        take(s,'ir_primer_piso')
        self.assertFalse(next(x for x in s.observe()['actions'] if x['id']=='hablar_marcela')['enabled'])
        take(s,'volver_porteria');take(s,'cerrar_turno')
        self.assertEqual(s.observe()['content']['kind'],'choice')

    def test_tirada_visible_fija_antes_de_consecuencias(self):
        s=fresh();take(s,'tomar_turno');take(s,'saludar');take(s,'ir_puesto_b')
        advance(s,'probar_radio')
        v=s.observe();snap=s.export()
        self.assertEqual(v['content']['kind'],'pending_evaluation')
        self.assertEqual(v['content']['presentation'],'visible')
        self.assertNotIn('senal_clara',facts(s))
        self.assertNotIn('senal_confusa',facts(s))
        clone=restore_session(admitted(),snap)
        self.assertEqual(clone.observe(),v)
        advance(s,'continue');advance(clone,'continue')
        self.assertEqual(s.export(),clone.export())
        self.assertEqual(facts(s).count('radio_intervenida'),1)

    def test_reconocimiento_y_restauracion(self):
        s=fresh();take(s,'tomar_turno');take(s,'ponerse_a_trabajar')
        for _ in range(4):take(s,'esperar_hora')
        take(s,'cerrar_turno')
        advance(s,'mirar_fijo')
        v=s.observe();snap=s.export()
        self.assertEqual(v['content']['kind'],'pending_evaluation')
        self.assertEqual(v['content']['presentation'],'acknowledged')
        self.assertNotIn('mirada_sostenida',facts(s))
        clone=restore_session(admitted(),snap)
        self.assertEqual(clone.observe(),v)
        settle(s);settle(clone)
        self.assertEqual(s.export(),clone.export())
        self.assertEqual(s.export()['ending'],'escalera_azul')

    def test_rechazo_y_revision_obsoleta(self):
        s=fresh();before=s.export();v=s.observe()
        req={'session_id':v['session_id'],'revision':v['revision'],'action_id':'inventado'}
        self.assertEqual(s.act(req)['error']['code'],'INVALID_ACTION')
        self.assertEqual(before,s.export())
        take(s,'tomar_turno')
        self.assertEqual(s.act(req)['error']['code'],'STALE_PROJECTION')

    def test_rng_reproducible_entre_semillas(self):
        for i in (0,1):
            seed=f'{i:064x}'
            self.assertEqual(play('solo',seed).export(),play('solo',seed).export())

    def test_mary_y_reaccion_causal(self):
        state=saved('casete')
        self.assertEqual(state['mary']['missions']['noche_en_correos'],'completed')
        self.assertEqual(snapfacts(state).count('relato_concluido'),1)
        self.assertEqual(snapfacts(state).count('amabilidad_observada'),1)
        self.assertNotIn('horror_cerrado',snapfacts(saved('radio')))

    def test_compartir_proyeccion_sin_privados(self):
        s=fresh();take(s,'tomar_turno');take(s,'saludar')
        take(s,'ir_primer_piso');take(s,'hablar_marcela')
        projection=json.dumps(s.observe(),ensure_ascii=False)
        self.assertNotIn('secret',projection)
        self.assertNotIn('romantic_score',projection)


if __name__=='__main__':
    unittest.main()
