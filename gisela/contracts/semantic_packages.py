"""Validación semántica, separada por responsabilidad."""
from __future__ import annotations
if __package__:
    from .semantic_shared import *
else:  # Compatibilidad de ejecución directa desde contracts/
    from semantic_shared import *

def evaluation_operations(owner: dict, path: str):
    """Devuelve consecuencias declaradas en ramas, con sus rutas de origen."""
    for bi, branch in enumerate(owner.get('evaluation', {}).get('branches', [])):
        for i, op in enumerate(branch.get('effects', [])):
            yield op, pointer(path, 'evaluation', 'branches', bi, 'effects', i)


class PackagesMixin:
    """Grupo de comprobaciones packages de un mismo validador."""
    def all_operations(self, pkg: dict):
        """Recorre consecuencias del paquete."""
        for ni,node in enumerate(pkg['nodes']):
            for si,step in enumerate(node['steps']):
                p=pointer('nodes',ni,'steps',si)
                for i,op in enumerate(step.get('effects',[])):yield op,pointer(p,'effects',i)
                for oi,option in enumerate(step.get('options',[])):
                    for i,op in enumerate(option.get('effects',[])):yield op,pointer(p,'options',oi,'effects',i)
                for bi,branch in enumerate(step.get('branches',[])):
                    for i,op in enumerate(branch.get('effects',[])):yield op,pointer(p,'branches',bi,'effects',i)
                yield from evaluation_operations(step, p)
                for oi,option in enumerate(step.get('options',[])):
                    yield from evaluation_operations(option, pointer(p,'options',oi))
        for si,scene in enumerate(pkg['scenes']):
            for ai,action in enumerate(scene.get('actions',[])):
                for i,op in enumerate(action.get('effects',[])):yield op,pointer('scenes',si,'actions',ai,'effects',i)
                yield from evaluation_operations(action, pointer('scenes',si,'actions',ai))
            for ei,element in enumerate(scene.get('elements',[])):
                for ai,action in enumerate(element.get('actions',[])):
                    for i,op in enumerate(action.get('effects',[])):yield op,pointer('scenes',si,'elements',ei,'actions',ai,'effects',i)
                    yield from evaluation_operations(action, pointer('scenes',si,'elements',ei,'actions',ai))
        for ri,rule in enumerate(pkg['rules']):
            for i,op in enumerate(rule['effects']):yield op,pointer('rules',ri,'effects',i)
        for ci,card in enumerate(pkg['cards']):
            if card['kind']=='skill':
                for i,op in enumerate(card['play']['effects']):yield op,pointer('cards',ci,'play','effects',i)
                for oi,outcome in enumerate(card['play'].get('outcomes',[])):
                    for i,op in enumerate(outcome['effects']):yield op,pointer('cards',ci,'play','outcomes',oi,'effects',i)
            if card['kind']=='effect':
                for field in ('on_apply','on_expire'):
                    for i,op in enumerate(card.get(field,[])):yield op,pointer('cards',ci,field,i)


    def _check_card_and_nodes(self, pkg: dict) -> None:
        """Reparte las comprobaciones entre cartas, nodos, escenas y reglas."""
        self._check_cards(pkg)
        self._check_nodes(pkg)
        self._check_scenes(pkg)
        self._check_rules(pkg)
        for operation, path in self.all_operations(pkg):
            self.operation(operation, path)

    def _check_cards(self, pkg: dict) -> None:
        """Comprueba propiedades, estadísticas y reglas de cada carta."""
        for index, card in enumerate(pkg['cards']):
            path = pointer('cards', index)
            self._check_card_properties(card, path)
            if card['kind'] == 'character' and 'sofia' in card:
                scale = pkg['manifest'].get('sofia_scale', {'min':0, 'max':10})
                for name, value in card['sofia'].items():
                    if not scale['min'] <= value <= scale['max']:
                        self.report('STAT_RANGE', path + '/sofia/' + name, 'Base fuera de escala')
            if card['kind'] == 'skill':
                self._check_skill_card(card, path)
            if card['kind'] == 'effect' and 'expiration' in card:
                for i, expiry in enumerate(card['expiration']['clauses']):
                    point = pointer(path, 'expiration', 'clauses', i)
                    if 'when' in expiry:
                        self.condition(expiry['when'], point + '/when')
                    if 'on_fact' in expiry and expiry['on_fact'] not in self.facts:
                        self.report('UNKNOWN_FACT', point + '/on_fact', 'Hecho no declarado')

    def _check_card_properties(self, card: dict, path: str) -> None:
        """Comprueba valores por defecto y cotas declaradas en cartas."""
        if 'properties' not in card:
            return
        self.unique(card['properties'], path + '/properties')
        for index, field in enumerate(card['properties']):
            point = pointer(path, 'properties', index)
            self.check_type(field['initial'], field['type'], point + '/initial')
            if 'min' in field and 'max' in field and field['min'] > field['max']:
                self.report('PROPERTY_RANGE', point, 'min supera max')
            value = field['initial']
            if isinstance(value, (float, int)) and not isinstance(value, bool):
                if ('min' in field and value < field['min']) or ('max' in field and value > field['max']):
                    self.report('PROPERTY_RANGE', point + '/initial', 'Valor inicial fuera de límites')

    def _check_skill_card(self, card: dict, path: str) -> None:
        """Comprueba requisitos, desenlaces y retornos de habilidades."""
        play = card['play']
        if 'requires' in play:
            self.condition(play['requires'], path + '/play/requires')
        for index, outcome in enumerate(play.get('outcomes', [])):
            self.condition(outcome['when'], pointer(path, 'play', 'outcomes', index, 'when'))
        policies = card.get('return_policy', {}).get('when', [])
        for index, entry in enumerate(policies):
            self.condition(entry['if'], pointer(path, 'return_policy', 'when', index, 'if'))
        destinations = {entry['to'] for entry in policies if entry['if'] == {'constant':True}}
        if len(destinations) > 1:
            self.report('RETURN_POLICY_CONFLICT', path + '/return_policy/when',
                        'Dos destinos de retorno incondicionales')
        elif len(policies) > 1:
            self.warn('OUTCOME_OVERLAP_UNPROVEN', path + '/return_policy/when', 'No se puede probar exclusividad de condiciones')

    def _check_nodes(self, pkg: dict) -> None:
        """Comprueba pasos y destinos en cada nodo del paquete."""
        for index, node in enumerate(pkg['nodes']):
            path = pointer('nodes', index)
            self.unique(node['steps'], path + '/steps')
            for step_index, step in enumerate(node['steps']):
                self._check_step_semantic(step, node, pointer(path, 'steps', step_index))

    def _check_step_semantic(self, step: dict, node: dict, path: str) -> None:
        """Comprueba un solo paso y sus alternativas de navegación."""
        name = step['op']
        if name == 'dialogue':
            self.entity_ref(step['speaker'], 'character', RefLocation(path + '/speaker'))
        if name == 'scene' and step['scene'] not in self.scenes:
            self.report('UNKNOWN_SCENE', path + '/scene', 'Escena no declarada')
        if name == 'ending' and step['ending'] not in self.endings:
            self.report('UNKNOWN_ENDING', path + '/ending', 'Final no declarado')
        if name == 'choice':
            self.unique(step['options'], path + '/options')
            for index, option in enumerate(step['options']):
                point = pointer(path, 'options', index)
                for key in ('visible_if', 'enabled_if'):
                    if key in option:
                        self.condition(option[key], point + '/' + key)
                if 'next' in option:
                    self.destination(option['next'], node, point + '/next')
                if self.active_version in ('1.4', '1.5') and 'evaluation' in option:
                    self._check_evaluation(option['evaluation'], node, point + '/evaluation')
        if self.active_version in ('1.4', '1.5') and name == 'evaluate':
            self._check_evaluation(step['evaluation'], node, path + '/evaluation')
        self._check_step_destinations(step, node, path)

    def _check_step_destinations(self, step: dict, node: dict, path: str) -> None:
        """Valida saltos de pasos aleatorios, transiciones y condiciones."""
        name = step['op']
        if name == 'random':
            self.unique(step['branches'], path + '/branches')
            for index, branch in enumerate(step['branches']):
                if 'next' in branch:
                    self.destination(branch['next'], node, pointer(path, 'branches', index, 'next'))
        if name == 'transition':
            self.destination(step['next'], node, path + '/next')
        if name == 'condition':
            self.condition(step['test'], path + '/test')
            for side in ('then', 'else'):
                if side in step:
                    self.destination(step[side], node, path + '/' + side)

    def _check_initial_scene_location(self, pkg: dict) -> None:
        """Evita entradas exploratorias cuya ubicación contradice a ALBERTO."""
        entry = pkg['manifest']['entry']
        if 'scene' not in entry:
            return
        scene = self.scenes.get(entry['scene'])
        initial = pkg['initial_state']
        if not scene or 'location' not in scene or 'player_character' not in initial:
            return
        player = next((c for c in initial['characters']
                       if c['id'] == initial['player_character']), None)
        if player is not None and player['location'] != scene['location']:
            self.report('SCENE_LOCATION_MISMATCH', '/manifest/entry/scene',
                        'La entrada física no coincide con la posición inicial del protagonista')

    def _check_scenes(self, pkg: dict) -> None:
        """Comprueba procedencia local de actores, elementos y acciones."""
        for index, scene in enumerate(pkg['scenes']):
            path = pointer('scenes', index)
            if 'location' in scene:
                self.entity_ref(scene['location'], 'location', RefLocation(path + '/location'))
                if not isinstance(scene['location'], str) or scene['location'].startswith('$'):
                    self.report('UNBOUND_SCENE_LOCATION', path + '/location',
                                'Una escena física requiere un ID de lugar explícito')
            self.unique(scene.get('elements', []), path + '/elements')
            self._check_actor_duplicates(scene, path)
            self.unique(scene.get('actions', []), path + '/actions')
            for i, actor in enumerate(scene.get('actors', [])):
                point = pointer(path, 'actors', i)
                self.entity_ref(actor['character'], 'character', RefLocation(point + '/character'))
                if 'visible_if' in actor:
                    self.condition(actor['visible_if'], point + '/visible_if')
            for i, element in enumerate(scene.get('elements', [])):
                self._check_element(element, pointer(path, 'elements', i), scene.get('location'))
            for i, action in enumerate(scene.get('actions', [])):
                self._check_action(action, node=None, path=pointer(path, 'actions', i))

    def _check_actor_duplicates(self, scene: dict, path: str) -> None:
        """Detecta actores literales repetidos sin indexar consultas dinámicas."""
        seen = set()
        for index, actor in enumerate(scene.get('actors', [])):
            ref = actor['character']
            if not isinstance(ref, str) or ref.startswith('$'):
                continue
            if ref in seen:
                self.report('DUPLICATE_ACTOR', pointer(path, 'actors', index),
                            'Personaje declarado más de una vez')
            seen.add(ref)

    def _check_element(self, element: dict, path: str, place: str | None) -> None:
        """Comprueba el ámbito de acciones pertenecientes a un elemento."""
        if 'entity' in element:
            self.entity_ref(element['entity'], None, RefLocation(path + '/entity'))
            ref = element['entity']
            if not isinstance(ref, str) or ref.startswith('$'):
                self.report('UNBOUND_SCENE_ENTITY', path + '/entity',
                            'Elemento de escena requiere una instancia explícita')
            kind = self.instances.get(ref, (None,))[0] if isinstance(ref, str) else None
            if place and kind not in (None, 'character', 'object', 'location'):
                self.report('SCENE_NONSPATIAL_ENTITY', path + '/entity',
                            'Una escena física no muestra habilidades ni efectos como entidades')
            if place and kind == 'location' and ref != place:
                self.report('SCENE_REMOTE_LOCATION', path + '/entity',
                            'Un elemento físico no puede vincular otro lugar')
        if 'visible_if' in element:
            self.condition(element['visible_if'], path + '/visible_if')
        self.unique(element.get('actions', []), path + '/actions')
        for index, action in enumerate(element.get('actions', [])):
            self._check_action(action, node=None, path=pointer(path, 'actions', index))

    def _check_rules(self, pkg: dict) -> None:
        """Valida disparadores y condiciones declaradas en cada regla."""
        for index, rule in enumerate(pkg['rules']):
            path = pointer('rules', index)
            trigger = rule['trigger']
            name = trigger['on']
            if name == 'state_changed':
                self.lvalue_type(trigger['target'], path + '/trigger/target')
            if name == 'fact_recorded' and trigger['fact'] not in self.facts:
                self.report('UNKNOWN_FACT', path + '/trigger/fact', 'Hecho no declarado')
            if name == 'signal' and trigger['id'] not in self.signals:
                self.report('UNKNOWN_SIGNAL', path + '/trigger/id', 'Señal no declarada')
            if name == 'node_completed' and trigger['node'] not in self.nodes:
                self.report('UNKNOWN_NODE', path + '/trigger/node', 'Nodo no declarado')
            if name == 'effect_expired' and trigger['effect'] not in self.cards['effect']:
                self.report('UNKNOWN_CARD', path + '/trigger/effect', 'Efecto no declarado')
            if 'when' in rule:
                self.condition(rule['when'], path + '/when')


    def _check_action(self, action: dict, node: dict|None, path: str) -> None:
        """Comprueba procedencia y destino de una acción."""
        for k in ('visible_if','enabled_if'):
            if k in action:self.condition(action[k],path+'/'+k)
        if self.active_version in ('1.4', '1.5') and 'evaluation' in action:
            self._check_evaluation(action['evaluation'], node, path + '/evaluation')
        if 'next' in action:
            if 'step' in action['next']:
                self.report('INVALID_SCENE_DESTINATION',path+'/next','Una acción de escena no posee nodo actual para salto local')
            elif action['next']['node'] not in self.nodes:
                self.report('UNKNOWN_NODE',path+'/next','Nodo no declarado')


    def _check_language(self, pkg: dict) -> None:
        """Comprueba referencias de lengua y textos."""
        mani=pkg['manifest'];base=self.base_language;langs=mani.get('languages',[base])
        if base not in langs:self.report('LANGUAGE_BASE',pointer('manifest','languages'),'La lengua base debe figurar en languages')
        if len(langs)!=len(set(langs)):self.report('DUPLICATE_LANGUAGE',pointer('manifest','languages'),'Idioma duplicado')
        table=pkg.get('strings',{}).get(base,{})
        def visit(obj,path):
            """Recorre referencias de texto en una estructura declarativa."""
            if isinstance(obj,dict):
                if set(obj)=={'text_key'} and obj['text_key'] not in table:
                    self.report('MISSING_TEXT',path,'text_key no disponible en idioma base')
                for k,v in obj.items():visit(v,path+'/'+str(k))
            elif isinstance(obj,list):
                for i,v in enumerate(obj):visit(v,path+'/'+str(i))
        for k in ('nodes','cards','scenes','endings'):visit(pkg[k],'/'+k)
        for language in pkg.get('strings',{}):
            if language not in langs:self.report('UNDECLARED_LANGUAGE',pointer('strings',language),'Idioma no declarado')


    def _check_mary_refs(self, value, path: str) -> None:
        """Comprueba que MARY lea solo hechos y variables publicados."""
        if isinstance(value, list):
            for item in value:
                self._check_mary_refs(item, path)
            return
        if not isinstance(value, dict):
            return
        names = ([value['has_fact']] if 'has_fact' in value else [])
        if value.get('kind') == 'distinct':
            names.extend(value['facts'])
        if value.get('kind') == 'weighted':
            names.extend(value['weights'])
        for name in names:
            if name not in self.facts:
                self.report('UNKNOWN_FACT', path, f'MARY consulta hecho no declarado: {name}')
        if set(value) == {'value'}:
            key = value['value']
            scope, _, name = key.partition('.')
            if (scope, name) not in self.vars:
                self.report('UNKNOWN_VARIABLE', path, f'MARY consulta variable no declarada: {key}')
        for item in value.values():
            self._check_mary_refs(item, path)

    def _check_mary(self, package: dict) -> None:
        """Valida MARY en admisión y comprueba sus referencias declaradas."""
        if 'mary' not in package:
            return
        from mary import MaryError, compile_plan
        try:
            plan = compile_plan(package['mary'])
        except MaryError as exc:
            self.report('INVALID_MARY', '/mary', str(exc)); return
        for kind in ('objectives', 'missions'):
            for spec in plan[kind].values():
                self._check_mary_refs(spec, '/mary/' + kind + '/' + spec['id'])
                effect = spec.get('yield')
                if effect and effect['fact'] not in self.facts:
                    self.report('UNKNOWN_FACT', '/mary/' + kind + '/' + spec['id'],
                                'Yield de MARY usa hecho no declarado')

    def validate_package(self, package: dict) -> list[Diagnostic]:
        """Devuelve diagnósticos del paquete sin ejecutarlo."""
        self.issues=[]
        version = package.get('manifest', {}).get('format_version') if isinstance(package, dict) else None
        if not self.use_version(version):return self.issues[:]
        if not self.check_schema('package',package):return self.issues[:]
        if version in ('1.3','1.4','1.5'):self._check_traits_package(package)
        self._index_package(package)
        mani=package['manifest']; entry=mani['entry']
        if mani.get('sofia_scale',{'min':0,'max':10})['min'] > mani.get('sofia_scale',{'min':0,'max':10})['max']:
            self.report('STAT_SCALE','/manifest/sofia_scale','La escala debe tener min <= max')
        if 'node' in entry and entry['node'] not in self.nodes:self.report('UNKNOWN_NODE',pointer('manifest','entry'),'Entrada a nodo inexistente')
        if 'scene' in entry and entry['scene'] not in self.scenes:self.report('UNKNOWN_SCENE',pointer('manifest','entry'),'Entrada a escena inexistente')
        if 'current_scene' in package['initial_state'] and package['initial_state']['current_scene'] not in self.scenes:
            self.report('UNKNOWN_SCENE',pointer('initial_state','current_scene'),'Escena inicial inexistente')
        if 'scene' in entry and package['initial_state'].get('current_scene',entry['scene'])!=entry['scene']:
            self.report('INITIAL_SCENE_CONFLICT',pointer('initial_state','current_scene'),'Escena de entrada no coincide con initial_state')
        if 'player_character' in package['initial_state']:
            self.entity_ref(package['initial_state']['player_character'], 'character', RefLocation(pointer('initial_state','player_character')))
        self._check_instances(package['initial_state'],'initial_state')
        self._check_initial_scene_location(package)
        self._check_names(package['initial_state'].get('facts',[]), self.facts, ('initial_state/facts','Hecho'))
        if version in ('1.4', '1.5'):
            self._prepare_evaluations(package)
        self._check_card_and_nodes(package)
        self._check_language(package)
        self._check_mary(package)
        return self.issues[:]
