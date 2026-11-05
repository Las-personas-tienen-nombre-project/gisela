# Verificación — primera corrección pedagógica

Alcance: laboratorio reducido de fundamentos, dos guías transversales y enlaces a la documentación oficial. Esta verificación **no** es una regresión integral ni cubre las unidades 2–9.

- `00_base.package.json`: ADMITTED.
- `01_primera_decision.package.json`: ADMITTED; elecciones `abrir` y `seguir` ejecutadas con GLAUQUIR hasta finales distintos.
- `02_otra_decision.package.json`: ADMITTED; elecciones `abrir` y `seguir` ejecutadas con GLAUQUIR hasta finales distintos.
- Mutación temporal `next.node = nodo_inexistente`: REJECTED con `UNKNOWN_NODE`, conforme a lo esperado. El archivo inválido no forma parte de los paquetes entregados.
- `python tools/check_quality.py`: OK.
- `python tools/check_doc_links.py`: OK.

Los comandos de admisión se ejecutaron desde la raíz del repositorio con `PYTHONPATH=.`. La ejecución de GLAUQUIR utilizó `python tools/glauquir.py --package ... --auto --choose abrir|seguir`.

## Límites

Las soluciones existentes de unidades 2–8 permanecen sin cambios; no se ha revisado su cobertura mediante esta fase. Los ejemplos narrativos de la Unidad 1 usan la estructura oficial y no pretenden reconstruir todavía el combate de Tegularis. Unidad 9 pendiente.
