# C6 — Diagnóstico privado de selección y cobertura

La captura es **optativa**. No forma parte de `Observe`, de los recibos públicos, del estado de sesión ni de los digests de los paquetes.

```bash
python tools/tegularis_campaign_v077.py --count 20 --strategy attack --diagnostics
```

`--diagnostics` registra, para cada selección ejecutada, el primer candidato seleccionado y las razones de descarte de los candidatos efectivamente evaluados: `guard_false`, `missing_instance`, `passive`, `not_in_hand`, `requirements_false`, `selected`. Los posteriores al seleccionado se etiquetan `not_evaluated` y **no** se vuelven a evaluar. Una política sin selección registra `selected: null` (fallback).

El resultado de cada semilla incluye `decisions`, `decision_counts` y `coverage`. `summary.json` agrega `coverage`, `candidate_selection_counts`, `candidate_reason_counts` y `npc_candidates_not_selected_in_samples`. Esta última lista significa exclusivamente **no observadas en estas semillas**, no inalcanzables.

La cobertura registra `skill_played` confirmados (identificadores de instancia) y eventos `effect_started`/`effect_refreshed` confirmados (identificadores de efecto). No pretende demostrar que una habilidad haya causado un desenlace ni identificar efectos que no generan estos eventos.

Las decisiones se capturan durante la ejecución real, sin evaluar una condición por segunda vez. Solo se añaden a los resultados tras confirmarse la acción; las fallidas no contribuyen a la cobertura. Las capturas se aíslan mediante `ContextVar` y permanecen en el flujo local de autoría. **No habilitar la publicación indiscriminada de estos artefactos en una interfaz de jugador.**

Sin `--diagnostics` el comportamiento y formato previo de campañas se mantienen; las únicas adiciones de metadatos al resumen se limitan a `diagnostics_enabled: false`.

La paridad debe probarse mediante igualdad de los campos previos por semilla, con la misma semilla, estrategia y paquete; los informes auxiliares no sustituyen pruebas del motor ni certifican balance.
