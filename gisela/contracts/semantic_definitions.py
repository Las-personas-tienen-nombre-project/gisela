"""Validación semántica, separada por responsabilidad."""
from __future__ import annotations
try:
    from .semantic_shared import *
except ImportError:
    from semantic_shared import *

class DefinitionsMixin:
    """Grupo de comprobaciones definitions de un mismo validador."""
    def _index_package(self, pkg: dict) -> None:
        """Construye índices sin hacer comprobaciones de ejecución."""
        self.pkg = pkg
        self.base_language = pkg['manifest']['language']
        self.nodes = self.unique(pkg['nodes'], 'nodes')
        self.scenes = self.unique(pkg['scenes'], 'scenes')
        self.rules = self.unique(pkg['rules'], 'rules')
        self.endings = set(self.unique(pkg['endings'], 'endings'))
        self._index_cards(pkg['cards'])
        self._index_manifest(pkg['manifest'])
        self.instances = {}
        for group, kind in COLLECTION_KINDS.items():
            for index, item in enumerate(pkg['initial_state'][group]):
                self._put_instance(item, kind, pointer('initial_state', group, index, 'id'))
        self.implicit_created = {op['instance_id'] for op, _ in self.all_operations(pkg)
                                 if op.get('op') in ('create_instance', 'apply_effect')
                                 and op.get('instance_id')}

    def _index_cards(self, cards: list[dict]) -> None:
        """Detecta cartas duplicadas dentro de cada categoría."""
        self.cards = {kind: {} for kind in COLLECTION_KINDS.values()}
        for index, card in enumerate(cards):
            by_kind = self.cards[card['kind']]
            if card['id'] in by_kind:
                self.report('DUPLICATE_ID', pointer('cards', index, 'id'),
                            f'Carta {card["kind"]} repetida: {card["id"]}')
            by_kind[card['id']] = card

    def _index_manifest(self, manifest: dict) -> None:
        """Registra variables, relaciones y vocabulario declarados."""
        self.vars = {}
        for index, item in enumerate(manifest.get('variables', [])):
            key = (item['scope'], item['id'])
            if key in self.vars:
                self.report('DUPLICATE_ID', pointer('manifest', 'variables', index, 'id'),
                            f'Variable repetida {key}')
            self.vars[key] = item
            self.check_type(item['initial'], item['type'],
                            pointer('manifest', 'variables', index, 'initial'))
        self.relationship_fields = self.unique(manifest.get('relationship_fields', []),
                                               'manifest/relationship_fields')
        for index, item in enumerate(manifest.get('relationship_fields', [])):
            self.check_type(item['initial'], item['type'],
                            pointer('manifest', 'relationship_fields', index, 'initial'))
        self._index_vocabulary(manifest)

    def _index_vocabulary(self, manifest: dict) -> None:
        """Comprueba que hechos, proposiciones y señales tengan IDs únicos."""
        for key in ('facts', 'claims', 'signals'):
            values = manifest.get(key, [])
            for item in set(values):
                if values.count(item) > 1:
                    self.report('DUPLICATE_ID', pointer('manifest', key), f'{key}: {item} repetido')
        self.facts = set(manifest.get('facts', []))
        self.claims = set(manifest.get('claims', []))
        self.signals = set(manifest.get('signals', []))


    def _put_instance(self, item: dict, kind: str, path: str) -> None:
        """Registra un ID de instancia y rechaza duplicados."""
        instance_id = item['id']
        if instance_id in self.instances:
            self.report('DUPLICATE_INSTANCE', path, f'Instancia duplicada entre categorías: {instance_id}')
        self.instances[instance_id] = (kind, item)
        if item['card'] not in self.cards[kind]:
            self.report('UNKNOWN_CARD', path[:-3] + 'card', f'La definición {item["card"]} no es una carta {kind}')


    def check_type(self, value: Any, expected: str, path: str) -> None:
        """Comprueba un valor contra el tipo declarado."""
        if not type_compatible(data_type(value), expected):
            self.report('TYPE_MISMATCH', path, f'Se esperaba {expected}; se recibió {data_type(value) or "valor no escalar"}')


    def _check_names(self, values: list[str], known: set[str], detail: tuple) -> None:
        """Detecta referencias desconocidas."""
        path, kind = detail
        for i, value in enumerate(values):
            if value not in known:
                self.report('UNKNOWN_DEFINITION', pointer(path,i), f'{kind} no declarado: {value}')


    def _check_property_values(self, instance: dict, kind: str, path: str) -> None:
        """Comprueba propiedades contra su carta."""
        card = self.cards.get(kind, {}).get(instance['card'])
        if not card:return
        defs = {x['id']:x for x in card.get('properties',[])}
        for key,val in instance.get('properties',{}).items():
            if key not in defs:
                self.report('UNKNOWN_PROPERTY',path+'/properties/'+key,f'Propiedad no declarada en carta: {key}')
            else:
                spec = defs[key]
                self.check_type(val,spec['type'],path+'/properties/'+key)
                if isinstance(val,(float,int)) and not isinstance(val,bool):
                    if ('min' in spec and val<spec['min']) or ('max' in spec and val>spec['max']):
                        self.report('PROPERTY_RANGE',path+'/properties/'+key, f'{key} fuera de límites')


    def _check_instances(self, initial: dict, prefix: str) -> None:
        """Comprueba entidades y relaciones sin decidir su ciclo de vida."""
        locations = {item['id'] for item in initial['locations']}
        characters = {item['id'] for item in initial['characters']}
        active = set(self.instances)
        for group, kind in COLLECTION_KINDS.items():
            for index, item in enumerate(initial[group]):
                path = pointer(prefix, group, index)
                if kind in ('character', 'location', 'object'):
                    self._check_property_values(item, kind, path)
                self._check_instance(kind, item, (path, locations, characters, active))
        self._check_capacities(initial, prefix, characters)
        self._check_effect_stack(initial, prefix)
        self._check_relationships(initial, prefix, active)
        for scope in ('world', 'session'):
            self._check_vars(initial.get(scope + '_variables', {}), scope,
                             pointer(prefix, scope + '_variables'))

    def _check_instance(self, kind, item, detail: tuple) -> None:
        """Valida referencias obligatorias de una sola entidad."""
        path, locations, characters, active = detail
        if kind == 'character':
            self._check_character(item, path, locations)
        elif kind == 'object':
            if item.get('owner') and item['owner'] not in characters:
                self.report('INVALID_OWNER', path + '/owner', 'Dueño del objeto inexistente')
            if item.get('location') and item['location'] not in locations:
                self.report('UNKNOWN_LOCATION', path + '/location', 'Lugar del objeto inexistente')
        elif kind == 'skill' and item['character'] not in characters:
            self.report('UNKNOWN_CHARACTER', path + '/character', 'Titular inexistente')
        elif kind == 'effect':
            if item['target'] not in active:
                self.report('UNKNOWN_ENTITY', path + '/target', 'Objetivo del efecto inexistente')
            card = self.cards['effect'].get(item['card'])
            if card and card.get('modifiers') and item['target'] not in characters:
                self.report('WRONG_ENTITY_KIND', path + '/target',
                            'Modificador S.O.F.I.A. requiere personaje')
            if card and card.get('modifiers') and item['target'] in characters:
                target = self.instances[item['target']][1]
                character_card = self.cards['character'].get(target['card'], {})
                if 'sofia' not in character_card:
                    self.report('MISSING_SOFIA', path + '/target',
                                'El efecto modifica un personaje sin S.O.F.I.A.')

    def _check_character(self, item, path, locations) -> None:
        """Valida ubicación, saberes, creencias y escala de atributos."""
        if item['location'] not in locations:
            self.report('UNKNOWN_LOCATION', path + '/location', 'Ubicación inexistente')
        self._check_names(item.get('knowledge', []), self.facts, (path + '/knowledge', 'Hecho'))
        for key in item.get('beliefs', {}):
            if key not in self.claims:
                self.report('UNKNOWN_CLAIM', path + '/beliefs/' + key, 'Proposición no declarada')
        scale = self.pkg['manifest'].get('sofia_scale', {'min':0, 'max':10})
        card = self.cards['character'].get(item['card'], {})
        if item.get('stats') and 'sofia' not in card:
            self.report('MISSING_SOFIA', path + '/stats',
                        'Atributos actuales sin carta S.O.F.I.A.')
        for name, val in card.get('sofia', {}).items():
            if not scale['min'] <= val <= scale['max']:
                self.report('STAT_RANGE', path + '/card', f'Atributo base {name} fuera de escala')
        for name, val in item.get('stats', {}).items():
            if not scale['min'] <= val <= scale['max']:
                self.report('STAT_RANGE', path + '/stats/' + name,
                            f'Atributo actual {name} fuera de escala')

    def _check_capacities(self, initial, prefix, characters) -> None:
        """Comprueba cupos y declaraciones únicas de mano y reserva."""
        capacities = {}
        for index, item in enumerate(initial['capacities']):
            path = pointer(prefix, 'capacities', index)
            if item['character'] not in characters:
                self.report('UNKNOWN_CHARACTER', path + '/character', 'Personaje inexistente')
            if item['character'] in capacities:
                self.report('DUPLICATE_CAPACITY', path, 'Capacidades repetidas')
            capacities[item['character']] = item
        slots = Counter((item['character'], item['zone']) for item in initial['skills'])
        for (character, zone), number in slots.items():
            if character not in capacities:
                self.report('MISSING_CAPACITY', pointer(prefix, 'skills'), 'Falta capacidad')
            elif number > capacities[character][zone]:
                self.report('CAPACITY_EXCEEDED', pointer(prefix, 'skills'),
                            f'{character}: {zone} tiene {number}, máximo {capacities[character][zone]}')

    def _check_effect_stack(self, initial, prefix) -> None:
        """Comprueba efectos cuya carta exige unicidad por objetivo."""
        seen = set()
        for index, effect in enumerate(initial['effects']):
            card = self.cards['effect'].get(effect['card'])
            if card and card.get('stacking') == 'unique_per_target':
                pair = (effect['target'], effect['card'])
                if pair in seen:
                    self.report('EFFECT_STACKING', pointer(prefix, 'effects', index),
                                'Efecto unique_per_target duplicado')
                seen.add(pair)

    def _check_relationships(self, initial, prefix, active) -> None:
        """Valida referencias, tipos y unicidad de relaciones persistidas."""
        seen = set()
        for index, relation in enumerate(initial.get('relationships', [])):
            path = pointer(prefix, 'relationships', index)
            if relation['from'] not in active or relation['to'] not in active:
                self.report('UNKNOWN_ENTITY', path, 'Relación entre instancias inexistentes')
            spec = self.relationship_fields.get(relation['key'])
            if spec is None:
                self.report('UNKNOWN_RELATION', path + '/key', 'Campo no declarado')
            else:
                self.check_type(relation['value'], spec['type'], path + '/value')
            key = (relation['from'], relation['to'], relation['key'])
            if key in seen:
                self.report('DUPLICATE_RELATION', path, 'Relación duplicada')
            seen.add(key)


    def _check_vars(self, values: dict, scope: str, path: str) -> None:
        """Comprueba variables declaradas en un ámbito."""
        for key,val in values.items():
            declared=self.vars.get((scope,key))
            if not declared:self.report('UNKNOWN_VARIABLE',path+'/'+key,f'Variable no declarada: {scope}.{key}')
            else:self.check_type(val,declared['type'],path+'/'+key)
