"""Validación semántica, separada por responsabilidad."""

from __future__ import annotations

if __package__:
    from .semantic_shared import *
else:  # Compatibilidad de ejecución directa desde contracts/
    from semantic_shared import *


class ExpressionsMixin:
    """Grupo de comprobaciones expressions de un mismo validador."""

    def entity_ref(
        self, ref: Any, kind: str | set[str] | None, location: RefLocation
    ) -> None:
        """Resuelve el tipo de una referencia declarativa."""
        path, context = location.path, location.context
        if isinstance(ref, dict) and "parameter" in ref:
            spec = self._skill_parameter(path, ref["parameter"])
            if spec is None or spec["kind"] != "character":
                self.report(
                    "INVALID_PARAMETER",
                    path,
                    "Se requiere un parámetro character declarado",
                )
            return
        if isinstance(ref, dict) and "query" in ref:
            self._query_entity_ref(ref["query"], kind, location)
            return
        if isinstance(ref, str) and ref.startswith("$"):
            # Se conoce el vocabulario, pero sus ligaduras concretas son dinámicas.
            if ref not in ("$actor", "$target", "$selected_object", "$candidate"):
                self.report(
                    "UNSUPPORTED_CONTEXT", path, f"Contexto no especificado: {ref}"
                )
            elif ref == "$candidate" and context != "query":
                self.report(
                    "UNBOUND_CONTEXT",
                    path,
                    "$candidate solo está disponible dentro de consultas",
                )
            return
        if not isinstance(ref, str):
            return
        entry = self.instances.get(ref)
        if not entry:
            if ref not in self.implicit_created:
                self.report(
                    "UNKNOWN_ENTITY",
                    path,
                    f"Instancia sin definición ni creación explícita: {ref}",
                )
            else:
                self.warn(
                    "DYNAMIC_REFERENCE",
                    path,
                    f"{ref} se crea en ejecución; comprobar su disponibilidad en runtime",
                )
        elif kind and entry[0] not in ({kind} if isinstance(kind, str) else kind):
            self.report(
                "WRONG_ENTITY_KIND", path, f"Se esperaba {kind}; {ref} es {entry[0]}"
            )

    def _skill_parameter(self, path: str, name: str) -> dict | None:
        """Parámetros disponibles solo dentro de la carta que los declara."""
        import re

        match = re.match(r"^/cards/(\d+)/play/", path)
        if match is None:
            return None
        card = self.pkg["cards"][int(match.group(1))]
        if card.get("kind") != "skill":
            return None
        return next(
            (p for p in card["play"].get("parameters", []) if p["id"] == name), None
        )

    def value_type(self, value: dict, path: str, context: str = "") -> str | None:
        """Infiere el tipo de una expresión sin ejecutarla."""
        if "parameter" in value:
            spec = self._skill_parameter(path, value["parameter"])
            if spec is None:
                self.report(
                    "UNBOUND_PARAMETER",
                    path,
                    "Parámetro no declarado en esta habilidad",
                )
                return None
            return "integer" if spec["kind"] == "integer" else "string"
        if "math" in value:
            return self._arithmetic_type(value["math"], RefLocation(path, context))
        if "trait_total" in value:
            for index, participant in enumerate(value["trait_total"]["participants"]):
                self.entity_ref(
                    participant["entity"],
                    {"character", "object", "location"},
                    RefLocation(
                        path + f"/trait_total/participants/{index}/entity", context
                    ),
                )
            if "traits" not in self.pkg:
                self.report("TRAITS_MISSING", path, "Se requiere un catálogo TRAITS")
            return "integer"
        if "literal" in value:
            return data_type(value["literal"])
        if "var" in value:
            return self._variable_type(value["var"], path, context)
        if "stat" in value:
            ref = value["stat"]["character"]
            self.entity_ref(
                ref, "character", RefLocation(path + "/stat/character", context)
            )
            entry = self.instances.get(ref) if isinstance(ref, str) else None
            if entry and entry[0] == "character":
                card = self.cards["character"].get(entry[1]["card"], {})
                if "sofia" not in card:
                    self.report(
                        "MISSING_SOFIA", path, "Personaje sin atributos S.O.F.I.A."
                    )
            return "integer"
        if "relationship" in value or "property" in value:
            return self._entity_value_type(value, path, context)
        if "clock" in value:
            return "time"
        if "turn" in value:
            return "integer"
        return None

    def _variable_type(self, ref: dict, path: str, context: str) -> str | None:
        """Determina el tipo de variable por ámbito y definición de carta."""
        scope, key = ref["scope"], ref["key"]
        if scope in ("world", "session"):
            spec = self.vars.get((scope, key))
            if spec:
                return spec["type"]
            self.report(
                "UNKNOWN_VARIABLE", path, f"Variable no declarada: {scope}.{key}"
            )
            return None
        entity = ref.get("entity")
        if entity is None:
            self.warn("UNRESOLVED_TYPE", path, "Variable de instancia sin entidad")
            return None
        self.entity_ref(entity, scope, RefLocation(path + "/var/entity", context))
        entry = self.instances.get(entity) if isinstance(entity, str) else None
        if entry and entry[0] == scope:
            card = self.cards[scope].get(entry[1]["card"], {})
            spec = next((x for x in card.get("properties", []) if x["id"] == key), None)
            if spec:
                return spec["type"]
            self.report(
                "UNKNOWN_PROPERTY", path, f"Variable de instancia sin definición: {key}"
            )
        else:
            self.warn("UNRESOLVED_TYPE", path, "Tipo de entidad dinámica")
        return None

    def _entity_value_type(self, value: dict, path: str, context: str) -> str | None:
        """Determina tipos de relaciones y propiedades declaradas."""
        if "relationship" in value:
            relation = value["relationship"]
            for key in ("from", "to"):
                self.entity_ref(
                    relation[key],
                    None,
                    RefLocation(path + "/relationship/" + key, context),
                )
            spec = self.relationship_fields.get(relation["key"])
            if not spec:
                self.report("UNKNOWN_RELATION", path, "Campo de relación desconocido")
            return spec["type"] if spec else None
        prop = value["property"]
        self.entity_ref(
            prop["entity"], None, RefLocation(path + "/property/entity", context)
        )
        ref = prop["entity"]
        entry = self.instances.get(ref) if isinstance(ref, str) else None
        if entry:
            card = self.cards[entry[0]].get(entry[1]["card"], {})
            spec = next(
                (x for x in card.get("properties", []) if x["id"] == prop["key"]), None
            )
            if not spec:
                self.report(
                    "UNKNOWN_PROPERTY", path, f"Propiedad no declarada: {prop['key']}"
                )
            return spec["type"] if spec else None
        self.warn("UNRESOLVED_TYPE", path, "Propiedad de referencia dinámica")
        return None

    def lvalue_type(self, value: dict, path: str) -> str | None:
        """Infiere el tipo de un destino de escritura."""
        return self.value_type(value, path)

    @staticmethod
    def _valid_datetime(value: str) -> bool:
        """Comprueba una fecha y hora declarada."""
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None and parsed.utcoffset() is not None
        except (ValueError, TypeError):
            return False

    def condition(self, cond: dict, path: str, context: str = "") -> None:
        """Comprueba condiciones y delega su vocabulario a grupos pequeños."""
        if "all" in cond or "any" in cond:
            key = "all" if "all" in cond else "any"
            for i, item in enumerate(cond[key]):
                self.condition(item, pointer(path, key, i), context)
        elif "not" in cond:
            self.condition(cond["not"], path + "/not", context)
        elif "compare" in cond:
            self._condition_compare(cond["compare"], path, context)
        else:
            self._condition_entity(cond, path, context)

    def _condition_compare(self, cond: dict, path: str, context: str) -> None:
        """Rechaza comparaciones entre tipos que no son ordenables."""
        a = self.value_type(cond["left"], path + "/compare/left", context)
        b = self.value_type(cond["right"], path + "/compare/right", context)
        if (
            a == "time"
            and b == "string"
            and "literal" in cond["right"]
            and self._valid_datetime(cond["right"]["literal"])
        ):
            b = "time"
        if (
            b == "time"
            and a == "string"
            and "literal" in cond["left"]
            and self._valid_datetime(cond["left"]["literal"])
        ):
            a = "time"
        if a and b and not (a == b or {a, b} <= {"integer", "number"}):
            self.report("INCOMPATIBLE_COMPARISON", path, "Operandos incompatibles")
        if cond["op"] in ("lt", "lte", "gt", "gte") and "boolean" in (a, b):
            self.report("INCOMPATIBLE_COMPARISON", path, "Orden sobre booleanos")

    def _condition_entity(self, cond: dict, path: str, context: str) -> None:
        """Valida referencias y vocabulario de consultas sobre el mundo."""
        if "has_fact" in cond and cond["has_fact"] not in self.facts:
            self.report("UNKNOWN_FACT", path, "Hecho no declarado")
        if "knows" in cond or "believes" in cond:
            key = "knows" if "knows" in cond else "believes"
            query = cond[key]
            self.entity_ref(
                query["character"],
                "character",
                RefLocation(path + "/" + key + "/character", context),
            )
            vocabulary = self.facts if key == "knows" else self.claims
            item = query["fact"] if key == "knows" else query["claim"]
            if item not in vocabulary:
                self.report(
                    "UNKNOWN_FACT" if key == "knows" else "UNKNOWN_CLAIM",
                    path,
                    "No declarado",
                )
        if "owns" in cond or "at_location" in cond:
            self._condition_location(cond, path, context)
        if "has_trait" in cond:
            query = cond["has_trait"]
            self.entity_ref(
                query["entity"],
                {"character", "object", "location"},
                RefLocation(path + "/has_trait/entity", context),
            )
            known = {x["id"] for x in self.pkg.get("traits", {}).get("traits", [])}
            if query["trait"] not in known:
                self.report(
                    "UNKNOWN_TRAIT", path + "/has_trait/trait", "Rasgo no declarado"
                )
        if "has_skill" in cond or "has_effect" in cond:
            self._condition_card(cond, path, context)
        if "exists" in cond:
            query = cond["exists"]
            ref = {"query": query["query"]} if "query" not in query else query
            self.entity_ref(ref, None, RefLocation(path + "/exists", "query"))

    def _condition_location(self, cond: dict, path: str, context: str) -> None:
        """Comprueba ubicación y propiedad de objetos."""
        if "owns" in cond:
            query = cond["owns"]
            self.entity_ref(
                query["owner"], "character", RefLocation(path + "/owns/owner", context)
            )
            self.entity_ref(
                query["object"], "object", RefLocation(path + "/owns/object", context)
            )
        else:
            query = cond["at_location"]
            self.entity_ref(
                query["character"],
                "character",
                RefLocation(path + "/at_location/character", context),
            )
            self.entity_ref(
                query["location"],
                "location",
                RefLocation(path + "/at_location/location", context),
            )

    def _condition_card(self, cond: dict, path: str, context: str) -> None:
        """Comprueba cartas referidas por consultas de habilidad o efecto."""
        key = "has_skill" if "has_skill" in cond else "has_effect"
        query = cond[key]
        target = "character" if key == "has_skill" else "target"
        self.entity_ref(
            query[target],
            "character" if key == "has_skill" else None,
            RefLocation(path + "/" + key + "/" + target, context),
        )
        category = "skill" if key == "has_skill" else "effect"
        if query[category] not in self.cards[category]:
            self.report("UNKNOWN_CARD", path, "Definición de carta inexistente")

    def destination(self, value: dict, node: dict, path: str) -> None:
        """Comprueba el destino de un salto narrativo."""
        if "node" in value:
            if value["node"] not in self.nodes:
                self.report("UNKNOWN_NODE", path, "Nodo destino inexistente")
        elif "step" in value and value["step"] not in {s["id"] for s in node["steps"]}:
            self.report(
                "UNKNOWN_STEP",
                path,
                f"Paso destino {value['step']} inexistente en nodo {node['id']}",
            )

    def operation(self, op: dict, path: str) -> None:
        """Valida tipos, referencias y vocabulario de las consecuencias."""
        name = op["op"]
        if name == "advance_time_to":
            at = op["at"]
            if not self._valid_datetime(at):
                self.report("INVALID_TIME", path + "/at", "Destino temporal inválido")
        if name == "emit_message":
            for key, expression in op["values"].items():
                self.value_type(expression, path + "/values/" + key)
        if name in ("set", "add", "roll"):
            self._operation_value(op, path)
        if name in (
            "transfer",
            "move_character",
            "create_instance",
            "remove_instance",
            "assign_trait",
            "remove_trait",
        ):
            self._operation_entity(op, path)
        self._operation_narrative(op, path)
        self._operation_skill(op, path)

    def _operation_value(self, op: dict, path: str) -> None:
        """Comprueba compatibilidad del destino con un valor declarado."""
        name = op["op"]
        typ = self.lvalue_type(op.get("target", op.get("store")), path + "/target")
        if name == "roll":
            if typ and typ not in ("number", "integer"):
                self.report("TYPE_MISMATCH", path + "/store", "roll requiere un número")
            return
        val = self.value_type(op["value"], path + "/value")
        if name == "add":
            if typ and typ not in ("number", "integer"):
                self.report("TYPE_MISMATCH", path + "/target", "add necesita un número")
            if val and val not in ("number", "integer"):
                self.report("TYPE_MISMATCH", path + "/value", "add requiere un número")
        if name == "set" and typ and val and not type_compatible(val, typ):
            self.report("TYPE_MISMATCH", path, "Tipos incompatibles")
        if name == "add" and typ == "integer" and val == "number":
            self.report("TYPE_MISMATCH", path, "Un entero requiere redondeo explícito")

    def _operation_entity(self, op: dict, path: str) -> None:
        """Comprueba entidades y cartas de las operaciones de ciclo de vida."""
        name = op["op"]
        if name in ("assign_trait", "remove_trait"):
            self.entity_ref(
                op["entity"],
                {"character", "object", "location"},
                RefLocation(path + "/entity"),
            )
            known = {x["id"] for x in self.pkg.get("traits", {}).get("traits", [])}
            if op["trait"] not in known:
                self.report("UNKNOWN_TRAIT", path + "/trait", "Rasgo no declarado")
        if name == "transfer":
            self.entity_ref(op["object"], "object", RefLocation(path + "/object"))
            for field in ("from", "to"):
                self.entity_ref(
                    op[field],
                    {"character", "location"},
                    RefLocation(path + "/" + field),
                )
        if name == "move_character":
            self.entity_ref(
                op["character"], "character", RefLocation(path + "/character")
            )
            self.entity_ref(op["location"], "location", RefLocation(path + "/location"))
        if name == "remove_instance":
            self.entity_ref(op["instance"], None, RefLocation(path + "/instance"))
        if name == "create_instance":
            self._operation_create(op, path)

    def _operation_create(self, op: dict, path: str) -> None:
        """Comprueba las ligaduras necesarias para crear una entidad."""
        candidates = [
            k
            for k in ("character", "location", "object")
            if op["card"] in self.cards[k]
        ]
        if len(candidates) != 1:
            self.report(
                "UNKNOWN_CARD", path + "/card", "Carta de clase ambigua o desconocida"
            )
        if len(candidates) == 1:
            kind = candidates[0]
            if kind == "character" and "location" not in op:
                self.report("MISSING_LOCATION", path, "Personaje sin ubicación")
            if kind == "object" and ("owner" in op) == ("location" in op):
                self.report("AMBIGUOUS_LOCATION", path, "Objeto requiere dueño o lugar")
            if kind == "location" and ("owner" in op or "location" in op):
                self.report(
                    "INVALID_CREATION", path, "Lugar no necesita dueño ni lugar"
                )
        if "instance_id" in op and op["instance_id"] in self.instances:
            self.report(
                "INSTANCE_COLLISION", path + "/instance_id", "ID utilizado al inicio"
            )
        if "owner" in op and "location" in op:
            self.report("AMBIGUOUS_LOCATION", path, "Dueño y lugar simultáneos")
        for key, kind in (("owner", "character"), ("location", "location")):
            if key in op:
                self.entity_ref(op[key], kind, RefLocation(path + "/" + key))

    def _operation_narrative(self, op: dict, path: str) -> None:
        """Comprueba hechos, creencias, escenas y señales."""
        name = op["op"]
        if name in ("record_fact", "learn_fact"):
            if op["fact"] not in self.facts:
                self.report("UNKNOWN_FACT", path + "/fact", "Hecho no declarado")
            if name == "learn_fact":
                self.entity_ref(
                    op["character"], "character", RefLocation(path + "/character")
                )
            else:
                for key, value in op.get("payload", {}).items():
                    self.value_type(value, path + "/payload/" + key)
        if name == "set_belief":
            self.entity_ref(
                op["character"], "character", RefLocation(path + "/character")
            )
            if op["claim"] not in self.claims:
                self.report(
                    "UNKNOWN_CLAIM", path + "/claim", "Proposición no declarada"
                )
        if name == "set_scene" and op["scene"] not in self.scenes:
            self.report("UNKNOWN_SCENE", path + "/scene", "Escena no declarada")
        if name == "emit_signal" and op["id"] not in self.signals:
            self.report("UNKNOWN_SIGNAL", path + "/id", "Señal no declarada")

    def _operation_skill(self, op: dict, path: str) -> None:
        """Comprueba habilidades y efectos declarados, sin ejecutarlos."""
        name = op["op"]
        if name in ("grant_skill", "move_skill", "discard_skill"):
            self.entity_ref(
                op["character"], "character", RefLocation(path + "/character")
            )
            if name == "grant_skill":
                if op["skill"] not in self.cards["skill"]:
                    self.report(
                        "UNKNOWN_CARD", path + "/skill", "Habilidad no declarada"
                    )
            else:
                self.entity_ref(
                    op["skill_instance"], "skill", RefLocation(path + "/skill_instance")
                )
        if name == "contest":
            self._operation_contest(op, path)
        if name == "play_skill":
            self.entity_ref(
                op["skill_instance"],
                "skill",
                RefLocation(path + "/skill_instance"),
            )
            self._validate_skill_arguments(op, path)
        if name == "play_first_skill":
            for index, candidate in enumerate(op["candidates"]):
                point = f"{path}/candidates/{index}"
                self.entity_ref(
                    candidate["skill_instance"],
                    "skill",
                    RefLocation(point + "/skill_instance"),
                )
                if "when" in candidate:
                    self.condition(candidate["when"], point + "/when")
                self._validate_skill_arguments(candidate, point)
        if name == "apply_effect":
            effect = self.cards["effect"].get(op["effect"])
            if effect is None:
                self.report("UNKNOWN_CARD", path + "/effect", "Efecto no declarado")
            kind = "character" if effect and effect.get("modifiers") else None
            self.entity_ref(op["target"], kind, RefLocation(path + "/target"))
        if name == "end_effect":
            self.entity_ref(
                op["effect_instance"], "effect", RefLocation(path + "/effect_instance")
            )

    def _validate_skill_arguments(self, invocation: dict, path: str) -> None:
        """Comprueba firmas declarativas, sin ejecutar ni inferir decisiones de NPC."""
        ident = invocation["skill_instance"]
        entry = self.instances.get(ident)
        if entry is None or entry[0] != "skill":
            return  # El diagnóstico de instancia ya lo emitió entity_ref.
        card = self.cards["skill"].get(entry[1]["card"])
        if card is None:
            return
        specs = {p["id"]: p for p in card["play"].get("parameters", [])}
        supplied = invocation.get("arguments", {})
        if set(specs) != set(supplied):
            self.report("INVALID_PARAMETERS", path, "Firma de argumentos incompatible")
        for name, expression in supplied.items():
            typ = self.value_type(expression, path + "/arguments/" + name)
            spec = specs.get(name)
            if spec is None:
                continue
            expected = "integer" if spec["kind"] == "integer" else "string"
            if typ and typ != expected:
                self.report(
                    "TYPE_MISMATCH",
                    path + "/arguments/" + name,
                    "Tipo de argumento incorrecto",
                )
            if spec["kind"] == "character" and "literal" in expression:
                self.entity_ref(
                    expression["literal"],
                    "character",
                    RefLocation(path + "/arguments/" + name),
                )
            if spec["kind"] == "integer" and "literal" in expression:
                val = expression["literal"]
                if type(val) is int and (
                    ("min" in spec and val < spec["min"])
                    or ("max" in spec and val > spec["max"])
                ):
                    self.report(
                        "PROPERTY_RANGE",
                        path + "/arguments/" + name,
                        "Argumento fuera de límites",
                    )

    def _query_entity_ref(self, q, kind, location):
        path, context = location.path, location.context
        if kind and q["kind"] not in ({kind} if isinstance(kind, str) else kind):
            self.report(
                "WRONG_ENTITY_KIND",
                path,
                "Consulta de entidad con categoría incompatible",
            )
        if q["selection"] == "all" and context != "query":
            self.report(
                "PLURAL_REFERENCE",
                path,
                "Una operación con referencia singular no acepta selection=all",
            )
        self.condition(q["where"], path + "/query/where", "query")

    def _arithmetic_type(self, formula, location):
        path, context = location.path, location.context
        a = self.value_type(formula["left"], path + "/math/left", context)
        b = self.value_type(formula["right"], path + "/math/right", context)
        if a and a not in ("integer", "number") or b and b not in ("integer", "number"):
            self.report("TYPE_MISMATCH", path, "La aritmética requiere números")
        return "number" if "number" in (a, b) else "integer" if a and b else None

    def _operation_contest(self, op, path):
        if op["profile"] not in {p["id"] for p in self.pkg.get("dice_profiles", [])}:
            self.report(
                "UNKNOWN_DICE_PROFILE", path + "/profile", "Perfil DICE inexistente"
            )
        for side in ("left", "right"):
            entry = op[side]
            typ = self.value_type(entry["base"], path + "/" + side + "/base")
            if typ and typ not in ("number", "integer"):
                self.report(
                    "TYPE_MISMATCH",
                    path + "/" + side + "/base",
                    "Base debe ser numérica",
                )
            for index, participant in enumerate(
                entry.get("context", {}).get("participants", [])
            ):
                self.entity_ref(
                    participant["entity"],
                    {"character", "object", "location"},
                    RefLocation(f"{path}/{side}/context/participants/{index}/entity"),
                )
