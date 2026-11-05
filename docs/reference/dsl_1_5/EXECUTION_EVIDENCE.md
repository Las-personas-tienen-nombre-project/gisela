# Verified reference examples

Source package: `gisela/packages/ejemplo_minimo.package.json`. This is a complete executable JSON package. Run with `PYTHONPATH=. python docs/reference/dsl_1_5/verify_reference_examples.py` from the repository root. These examples are automated checks of the public package admission, session, Observe, Act and restore APIs. They are not proof of every DSL mechanism.

- PASS action abrir step 0
- PASS action abrir step 1
- PASS action abrir step 2
- PASS ending abrir
- PASS action seguir step 0
- PASS action seguir step 1
- PASS action seguir step 2
- PASS ending seguir
- PASS observe pure
- PASS unoffered action rejected without mutation
- PASS stale action rejected without mutation
- PASS restore same observe
- PASS same action after restore
- PASS equal seed equal initial state
- PASS wrong format rejected: UNSUPPORTED_VERSION
- PASS dangling node rejected: UNKNOWN_NODE
