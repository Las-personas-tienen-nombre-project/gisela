# Resultados — Unidad 5 (habilidades)

Base productiva de solo lectura: `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`.

## Controles realizados

- Admisión pública `gisela.contracts.admit_package_file`: **5/5 ejercicios admitidos** y **5/5 solucionarios admitidos**.
- Rechazo semántico deliberado de la variable inexistente en el sexto ejercicio: **confirmado**.
- Comparación de propiedades trabajadas: los cinco ejercicios contienen una alteración respecto de la base; cada solucionario coincide íntegramente con el paquete de referencia: **5/5**.
- `python -m unittest gisela.engine.tests.test_h34d_skills -q`: **17 pruebas, OK**.
- `python -m gisela.cli.glauquir --auto --actuation --rounds 1 --package workshops/autoria_dsl_15/soluciones/05_habilidades/01_slash_tp.package.json`: ejecución de **1 ronda completada**, salida terminada con `Laboratorio completado: 1 rondas verificables.`

## Alcance y limitaciones

La admisión semántica y el contraste contra el canon prueban que las declaraciones están bien formadas y los solucionarios restituyen lo previsto; **no** prueban que cada rama de acierto, fallo o empate haya ocurrido en esa partida. La ejecución de una ronda demuestra que el paquete es ejecutable mediante GLAUQUIR, no que sus cinco modificaciones hayan sido ejercitadas dinámicamente. Las 17 pruebas existentes son regresión focalizada de habilidades, no una nueva prueba de cobertura de todas las ramas de estos ejercicios. No se ejecutó la batería general del repositorio ni cinco recorridos completos separados.

Reproducción de controles: `PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_unidad_05.py`. La herramienta es del instructor y no requiere que el alumno programe.
