"""Puerta pública de validación semántica GISELA v1.2."""
from __future__ import annotations
try:
    from .semantic_shared import *
    from .semantic_definitions import DefinitionsMixin
    from .semantic_expressions import ExpressionsMixin
    from .semantic_packages import PackagesMixin
    from .semantic_sessions import SessionsMixin
except ImportError:
    from semantic_shared import *
    from semantic_definitions import DefinitionsMixin
    from semantic_expressions import ExpressionsMixin
    from semantic_packages import PackagesMixin
    from semantic_sessions import SessionsMixin

try:
    from .semantic_traits import TraitsMixin
except ImportError:
    from semantic_traits import TraitsMixin

try:
    from .semantic_evaluations import EvaluationsMixin
except ImportError:
    from semantic_evaluations import EvaluationsMixin

from functools import lru_cache


@lru_cache(maxsize=4)
def _load_versions(schema_root: Path) -> dict:
    """Carga contratos versionados; v1.4 solo es admisión E1."""
    specs = {p.name.removesuffix('.schema.json'): json.loads(p.read_text(encoding='utf8'))
         for p in schema_root.glob('*.schema.json')}
    if len(specs) != 13:
        raise ValueError(f'Se esperaban 13 schemas v1.2; se encontraron {len(specs)}')
    next_specs = {p.name.removesuffix('.schema.json'): json.loads(p.read_text(encoding='utf8'))
              for p in (schema_root / 'v1_3').glob('*.schema.json')}
    if len(next_specs) != 13:
        raise ValueError('Se esperaban 13 schemas v1.3')
    from traits.contracts import SCHEMA as traits_schema
    from dice.core import SCHEMA as dice_schema
    third_specs = {p.name.removesuffix('.schema.json'): json.loads(p.read_text(encoding='utf8'))
                   for p in (schema_root / 'v1_4').glob('*.schema.json')}
    if len(third_specs) != 13:
        raise ValueError('Se esperaban 13 schemas v1.4')
    fourth_specs = {p.name.removesuffix('.schema.json'): json.loads(p.read_text(encoding='utf8'))
                    for p in (schema_root / 'v1_5').glob('*.schema.json')}
    if len(fourth_specs) != 13:
        raise ValueError('Se esperaban 13 schemas v1.5')
    registry = Registry().with_resources((s['$id'], Resource.from_contents(s))
            for s in [*specs.values(), *next_specs.values(), *third_specs.values(), *fourth_specs.values(), traits_schema, dice_schema])
    return {
        '1.2': {k: Draft202012Validator(v, registry=registry, format_checker=FormatChecker()) for k,v in specs.items()},
        '1.3': {k: Draft202012Validator(v, registry=registry, format_checker=FormatChecker()) for k,v in next_specs.items()},
        '1.4': {k: Draft202012Validator(v, registry=registry, format_checker=FormatChecker()) for k,v in third_specs.items()},
        '1.5': {k: Draft202012Validator(v, registry=registry, format_checker=FormatChecker()) for k,v in fourth_specs.items()}}


class Validator(EvaluationsMixin, TraitsMixin, DefinitionsMixin, ExpressionsMixin, PackagesMixin, SessionsMixin):
    """Valida documentos sin ejecutar historias ni comprometer estado."""
    def __init__(self, schema_root: Path = ROOT):
        """Carga schemas locales y prepara índices de validación."""
        self.schema_versions = _load_versions(schema_root)
        self.active_version = '1.2'
        self.schemas = self.schema_versions['1.2']
        self.issues: list[Diagnostic] = []
        self.pkg: dict = {}
        self.cards: dict[str, dict[str, dict]] = {}
        self.instances: dict[str, tuple[str, dict]] = {}
        self.nodes: dict[str, dict] = {}
        self.scenes: dict[str, dict] = {}
        self.endings: set[str] = set()
        self.rules: dict[str, dict] = {}
        self.vars: dict[tuple[str, str], dict] = {}
        self.relationship_fields: dict[str, dict] = {}
        self.facts: set[str] = set()
        self.claims: set[str] = set()
        self.signals: set[str] = set()
        self.implicit_created: set[str] = set()
        self.base_language: str = ''


    def report(self, code: str, path: str, message: str) -> None:
        """Agrega un diagnóstico tipado."""
        self.issues.append(Diagnostic('error', code, path, message))

    def warn(self, code: str, path: str, message: str) -> None:
        """Registra una advertencia no bloqueante, sin parámetros implícitos."""
        self.issues.append(Diagnostic('warning', code, path, message))


    def use_version(self, version: str) -> bool:
        if version not in self.schema_versions:
            self.report('UNSUPPORTED_VERSION', '/manifest/format_version', 'Versión no admitida')
            return False
        self.active_version = version
        self.schemas = self.schema_versions[version]
        return True

    def check_schema(self, kind: str, document: dict) -> bool:
        """Comprueba la forma JSON Schema y registra errores."""
        errs = sorted(self.schemas[kind].iter_errors(document), key=lambda e: tuple(map(str, e.absolute_path)))
        for err in errs:
            self.report('SCHEMA_INVALID', pointer(*err.absolute_path), f'{kind}: {err.message}')
        return not errs


    def unique(self, data: list[dict], prefix: str, name: str = 'id') -> dict[str, dict]:
        """Indexa identificadores y registra duplicados."""
        out = {}
        for i, obj in enumerate(data):
            key = obj[name]
            if key in out: self.report('DUPLICATE_ID', pointer(prefix, i, name), f'ID repetido: {key}')
            out[key] = obj
        return out





def strict_object_pairs(pairs):
    """Rechaza claves duplicadas al construir un objeto JSON."""
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f'Clave JSON duplicada: {key}')
        out[key] = value
    return out


def load_json_strict(path: Path) -> Any:
    """Lee JSON sin duplicados ni números no finitos."""
    return json.loads(path.read_text(encoding='utf8'), object_pairs_hook=strict_object_pairs,
                      parse_float=__import__('decimal').Decimal,
                      parse_constant=lambda c: (_ for _ in ()).throw(ValueError(f'Constante JSON no permitida: {c}')))


def cli():
    """Ejecuta la validación semántica offline desde la línea de comandos."""
    p=argparse.ArgumentParser(description='Validador semántico estático GISELA v1.2')
    p.add_argument('package',type=Path,help='Paquete autoral JSON')
    p.add_argument('--session',type=Path,help='Snapshot de sesión JSON')
    p.add_argument('--expected-digest',help='Digest obtenido de forma confiable por anfitrión (64 hex)')
    p.add_argument('--json',action='store_true',help='Emitir diagnósticos JSON')
    args=p.parse_args()
    try:
        pkg=load_json_strict(args.package)
        session=load_json_strict(args.session) if args.session else None
        engine=Validator()
        out=engine.validate_package(pkg)
        if session is not None and not any(d.severity=='error' for d in out):
            out+=engine.validate_session(session,pkg,args.expected_digest)
    except (OSError, ValueError, json.JSONDecodeError) as ex:
        print(f'Error de entrada: {ex}',file=sys.stderr);return 2
    if args.json:
        print(json.dumps({'valid':not any(d.severity=='error' for d in out),
                          'diagnostics':[asdict(d) for d in out]},ensure_ascii=False,indent=2))
    else:
        for d in out:print(f'{d.severity.upper()} {d.code} {d.path}: {d.message}')
        print(f'{sum(d.severity=="error" for d in out)} errores, {sum(d.severity=="warning" for d in out)} advertencias')
    return 1 if any(d.severity=='error' for d in out) else 0


if __name__=='__main__':sys.exit(cli())
