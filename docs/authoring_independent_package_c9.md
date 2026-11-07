# C9: standalone package authoring example

`tools/build_night_shift_authoring.py` builds a **new** DSL 1.5 package without
reading any published package as a starting template. The example has two
choices, two endings, session variables, one fact, and one fact reaction.

From the repository root:

```sh
python tools/build_night_shift_authoring.py --check
python tools/check_generated.py
python -m pytest -q gisela/engine/tests/test_independent_narrative_c9.py
```

An intentional authoring change can be materialized with
`python tools/build_night_shift_authoring.py --write`. The write replaces only
one generated file atomically; it does not imply multi-file transactionality.
Review that JSON change in version control, then verify admission and tests.

`tools/authoring_package.py` only constructs the JSON sections and copies
inputs. It is not a substitute for `admit_package()`. Package metadata and
initial session variable values are explicit and must agree. There is no new
runtime syntax, parser, interpretation of author code, or dependency from the
engine to the authoring tools. This is a narrow proof of independent package
construction, not a general scene editor or world-building API.
