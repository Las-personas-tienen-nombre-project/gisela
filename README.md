# GISELA. Interactive story engine

GISELA means _enGine for Interactive Stories through Events, Links, and Actions_. GISELA is an independent general engine for declared interactive narratives. This repository contains the engine, its independent libraries, CLI client GLAUQUIR, tests, documentation, and example narrative packages. The Ren'Py integration belongs to a separate demo repository; it is not required to use GISELA.

This README explains the current implementation. For design history and architecture decisions, use the links at the end. The older documents describe important decisions but some were written before later features were implemented.

## What GISELA does

GISELA admits JSON packages, starts and restores sessions, exposes a player view, accepts authorized actions, evaluates rules, applies world changes, processes reactions, advances the narrative, and saves the confirmed result. Every action is checked against the actions offered by the current observation.

A story package contains the world definitions and declared story behavior. The engine does not execute arbitrary author Python code. GISELA is the only authority for the session, its current node and scene, transactions, time, and deterministic random state.

## Main parts

ALBERTO is the internal world model for characters, places, objects, knowledge, relations, skills, effects, and traits assigned to entities. S.O.F.I.A. is an optional set of five numerical attributes. TRAITS is an independent library for contextual trait contributions. DICE is an independent mathematical evaluator. MARY is an independent mission and objective evaluator. The narrative conditions package provides shared logical operations.

GLAUQUIR is the bundled CLI client. A Ren'Py adapter exists in the separate demo project. Clients show public content and send requests through the authorized client boundary; they do not decide world consequences or commit changes. For formal names and individual guides, read [Names and responsibilities](docs/reference/NAMING.md).

## Start an adventure

Install the development requirements from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Run the independent test adventure with the installed GLAUQUIR command.

```bash
glauquir --package gisela/packages/h46_faro_de_niebla.package.json
```

Run the Central Clasificadora test adaptation.

```bash
glauquir --package gisela/packages/h46b_central_clasificadora.package.json
```

The game text and current client commands are in Spanish. This does not change the language of the engine contracts. For an interactive walkthrough, read [Quick start](docs/guides/QUICK_START.md). The CLI `--auto` mode is not a guaranteed route to an ending for the Faro and Central packages; use the scripted walkthroughs with `--verify-restores` for acceptance.

Validate an author package with `gisela validate historia.package.json`. Add `--json` for structured diagnostics. Running `glauquir` without `--package` uses its bundled default story, including from outside this repository.

## Admission before execution

Every package must be admitted before use. Admission checks JSON structure, semantic references, and other declared constraints. It produces a package digest and frozen definitions. Admission does not create a session and does not calculate future state dependent values prematurely.

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json
```

The admission API is in `gisela.contracts.admit_package`. Use `admit_package_file` for strict file loading or `admit_package` for already loaded definitions. The caller is responsible for rejecting duplicate keys before passing an already parsed dictionary.

A valid schema does not mean every possible operation is executable. The engine also checks whether it supports the admitted operations. Authors should use existing admitted packages and executable tests as references.

## Session lifecycle

Create a session from an admitted package. GISELA initializes the world and enters the declared starting point. It then runs automatic steps until it reaches a public action, a pending decision, a visible evaluation, or the end of the session.

Observe returns the public view of the current confirmed state. It contains a revision, visible content, and a list of offered actions. Act takes the current session identifier, revision, and a currently offered action identifier. It does not accept arbitrary world operations from a client. For example:

```python
view = session.observe()
action = next(a for a in view['actions'] if a['enabled'])
reply = session.act({
    'session_id': view['session_id'],
    'revision': view['revision'],
    'action_id': action['action_id'],
})
if reply['status'] != 'ok':
    print(reply)  # Act returns an error dictionary instead of raising it.
```

A session bound to `ExecutionGateway` rejects direct `session.act()` calls; its authenticated clients use the gateway's command interface instead. See [Client API](docs/architecture/API_CLIENTES.md) for the full contract.

A successful action runs against a draft. GISELA resolves conditions, world effects, reactions, objectives, and narrative transitions before committing. A failed action leaves the previous confirmed state unchanged. Repeated or stale requests cannot be used to bypass the authorization boundary.

A turn is associated with executing a narrative node. It is not necessarily one client command or one dice evaluation. Scene exploration can advance fictional time through declared effects without defining an extra narrative turn.

## Python session example

The following sample uses the public session API. It starts a package and reads the first public view. It does not make assumptions about which action the author will offer.

```python
from pathlib import Path
from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

source = Path("gisela/packages/h46_faro_de_niebla.package.json")
admitted = admit_package_file(source)
session = new_session(admitted)
view = session.observe()
print(view["status"])
print(view["actions"])
snapshot = session.export()
restored = restore_session(admitted, snapshot)
assert restored.export() == snapshot
```

An optional boundary for authenticated external clients is `ExecutionGateway` from `gisela.engine.authorized_gateway`. The gateway binds trusted client identities and their granted capabilities. Do not take the principal identity from untrusted Act input. The host is responsible for authenticating a caller before binding it.

## Hidden and visible DICE evaluations

DICE is a pure numerical library. GISELA resolves effective values, calls DICE through its own reproducible random source, chooses the declared branch, and applies its effects.

A hidden evaluation resolves within the action transaction. A visible or acknowledged evaluation fixes the result and random state, then exposes a pending evaluation without applying its branch consequences. The client later chooses the offered continuation action. Saving or restoring must not roll new dice for that pending result. Several visible results can be preserved in an ordered replay when a causal operation contains multiple evaluation points.

The default public view of a pending evaluation exposes the result category and dice only. Private attributes and internal contributions are not published automatically. Refer to [Engine execution](gisela/engine/README.md) and [Contracts](gisela/contracts/README.md).

## Auxiliary decisions and replay

Some effects need an additional choice before the enclosing transaction can finish. GISELA preserves the causal request and reconstructs it on continuation using the recorded answers. A rejected branch does not commit a partial world change. A restore validates the pending operation against the same package.

Only one top level causal operation can be pending at a time. The pending evaluation and pending transaction mechanisms do not create independent session authorities.

## World state and progression

ALBERTO stores current entities and relations. Conditions can inspect allowed facts and other values. World operations on drafts can transfer objects, move characters, change current attributes, manage skills and effects, change assigned traits, and advance fictional time when declared and supported.

MARY observes authorized causal events and proposes mission progress and yields. GISELA is responsible for confirming those results alongside the original action. No library may commit a separate partial state.

## Save and restore

`session.export()` returns a deep copy of the confirmed session state. `restore_session` validates the saved structure, the admitted package digest, and the reconstructability of pending actions. Hosts manage storage. The exported data is not a player observation and must not be published to untrusted clients because it can contain private information.

The package digest prevents silently loading a save against changed definitions. It does not verify external artwork or sound files. Session migration across incompatible package versions is not automatic.

## Contracts and compatibility

Current packages use v1.5 for visible evaluation support. Earlier v1.2, v1.3, and v1.4 contracts remain present for compatibility. Do not assign v1.5 meaning to older saved sessions. JSON schemas and semantic validation are under `gisela/contracts`.

## Tests

Instale las dependencias de desarrollo desde la raíz del repositorio:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

El verificador oficial ejecuta pruebas del motor, contratos, bibliotecas y
herramientas, Ruff, Radon, Bandit, calidad estructural, enlaces e invariantes E0–E3:

```bash
python tools/check_gisela.py
```

Para añadir los seis recorridos narrativos y sus restauraciones:

```bash
python tools/check_gisela.py --full
```

Si el kit informa `No module named ruff`, `radon` o `bandit`, faltan
dependencias de desarrollo en el entorno virtual que ejecuta el script. Desde
la raíz del repositorio, instálelas y repita la verificación con ese mismo
intérprete:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python tools/check_gisela.py --full
```

El fallo de `tools/test_static_quality.py` también puede deberse a que Ruff no
está instalado en ese entorno. No es necesario cambiar las políticas estáticas
ni las pruebas para resolver una dependencia ausente.

Desde otro directorio, invoque la **ruta absoluta del script**; este localiza
internamente la raíz y ejecuta las comprobaciones desde allí. Los recorridos
requieren las dependencias de desarrollo indicadas en `requirements-dev.txt`.
Ruff, la complejidad D–F y los hallazgos Bandit bloqueantes hacen fallar el kit.
El índice MI y las 19 advertencias Bandit Low revisadas en pruebas son informativos.
La guía de verificación y sus límites están en
[Verificación independiente](docs/guides/VERIFICACION_GISELA.md).

## Versioning and releases

GISELA is versioned and published independently from its clients, including the Ren'Py demo. The Python distribution version is declared in `pyproject.toml` under `[project] version`. Git release tags use the form `vX.Y.Z` and **must correspond exactly** to distribution version `X.Y.Z`. This is separate from narrative contract versions such as `v1.5`: changing the Python package version does not automatically change a schema contract.

### Prepare a release

1. Work on a branch and review the intended changes. Update `[project] version` in `pyproject.toml` to the **new** distribution version, and update release-specific documentation where applicable.
2. Install development dependencies and run the official checks. Use `--full` when the release changes narrative behavior or compatibility. For releases that change packaged modules, resources, dependencies, or console commands, also verify installation from a wheel:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python tools/check_gisela.py
python tools/check_gisela.py --full
python tools/verify_cli_wheel.py
```

`verify_cli_wheel.py` builds a wheel, installs it with its dependencies into a fresh temporary virtual environment, and runs `glauquir` and `gisela validate` from outside the source tree. It needs access to dependency wheels or a package index. Resolve any failed check before tagging.

3. Build a wheel into a clean output directory and inspect its embedded metadata. The following commands check the version without trusting only the local `pyproject.toml`:

```bash
python -m pip wheel --no-deps --wheel-dir /tmp/gisela-release .
python - /tmp/gisela-release X.Y.Z <<'PYTHON'
from pathlib import Path
from email.parser import Parser
import sys
from zipfile import ZipFile

wheels = list(Path(sys.argv[1]).glob('gisela_narrative_engine-*.whl'))
if len(wheels) != 1:
    raise SystemExit(f'Expected one GISELA wheel; found {len(wheels)}')
with ZipFile(wheels[0]) as archive:
    files = [name for name in archive.namelist() if name.endswith('.dist-info/METADATA')]
    if len(files) != 1:
        raise SystemExit('Missing or ambiguous wheel metadata')
    info = Parser().parsestr(archive.read(files[0]).decode('utf-8'))
    version = info['Version']
    print(f"Distribution: {info['Name']} {version}")
    if version != sys.argv[2] or version != wheels[0].name.split('-')[1]:
        raise SystemExit('Wheel, metadata, and intended version differ')
PYTHON
```

Replace `X.Y.Z` with the intended new version. Use a newly emptied `/tmp/gisela-release` directory for each verification so an old wheel cannot be mistaken for the new release. `verify_cli_wheel.py` performs the separate installation check for the console commands.

### Publish the Git tag

After all required checks pass, review and stage only the intended changes, including any new files (`git add -- path/to/new-file` after `git add -p`). Then commit and push the release to the intended branch. Replace every `X.Y.Z` below with the new distribution version; tag the exact release commit:

```bash
git status --short
git add -p
git commit -m "release: GISELA X.Y.Z"
git push origin HEAD
git tag -a vX.Y.Z -m "GISELA vX.Y.Z"
git push origin vX.Y.Z
```

Verify the tag content after publication:

```bash
git show vX.Y.Z:pyproject.toml
```

**Never move or reuse a published release tag.** If a tag points to a commit whose package metadata is wrong, publish a correction under a new version and tag. For example, `v0.1.3` was published with distribution version `0.1.333`; the corrective release uses `v0.1.4` and `0.1.4`.

### Update downstream consumers

The Ren'Py demo pins GISELA to a specific Codeberg tag. When publishing a new GISELA version, update the demo's `pyproject.toml` and the `VERSION` and `SOURCE` declarations in `tools/build_renpy_h5.py`, then rebuild and verify with the real Ren'Py SDK. GISELA itself does not install or control Ren'Py. A future public PyPI release should be validated separately before consumers switch from Git references to a PyPI requirement.

### Native dependencies in Ren'Py consumers

The Ren'Py SDK carries its own Python runtime. Consumers embedding GISELA dependencies under Ren'Py's `python-packages` must select wheels compatible with that runtime's Python version, ABI, operating system, and architecture. A `cp314` extension cannot be loaded by CPython 3.12. Installing `pip` into the SDK is not necessary; the downstream build process is responsible for preparation and runtime tests.

With `referencing` and CPython 3.12, downstream packaging must also provide a suitable `typing_extensions` for `TypeVar(default=...)`. GISELA's semantic-contract imports preserve genuine missing-dependency errors rather than rewriting them as missing local modules. Direct execution of historical CLI modules continues to use the explicit `__package__` path.

## Known limits

The Ren'Py H5 bridge was implemented in the separate demo project and is not included in this repository. The real graphical SDK and exported builds still need acceptance testing. The Central Clasificadora adventure is a condensed narrative test, not an approved final script. Musical recordings, rights clearance, finished art, and distribution are outside this engine milestone.

## Further reading

Read [Engine implementation](gisela/engine/README.md) for transaction and source module details, [Contracts](gisela/contracts/README.md) for authoring formats, [Documentation index](docs/README.md) for learning paths, and [Current roadmap](docs/operatives/ROADMAP.md) for the implementation status.

Read ADR 020 for authorized callers, ADR 021 for evaluation authoring, ADR 022 for hidden evaluations, and ADR 023 for visible evaluations. These source decision records remain in `docs/decisions` in their original language. The implemented v1.5 design is recorded in `docs/architecture/E3_EVALUACIONES_VISIBLES.md`.


## License and Copyright

GISELA, its software components, development tools, and associated source code are licensed under the **Apache License, Version 2.0**. See the [LICENSE](LICENSE) file for details.

**Narrative content is excluded from the Apache 2.0 license.**

All stories, literary works, scenes, dialogue, original characters, and narrative packages included in this repository are **Copyright (c) 2026. All rights reserved.**

This includes demonstration and testing materials, such as *El faro de niebla* and *Las personas tienen nombre*, as well as any other narrative content provided with GISELA.

These materials are included solely for demonstration, development, and testing purposes. Their inclusion does not grant permission to modify, redistribute, republish, or commercially exploit them without prior authorization from the copyright holder.

This restriction does not affect the rights granted to the GISELA software under the Apache License 2.0.
