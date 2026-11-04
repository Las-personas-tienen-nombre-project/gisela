# Tegularis — Workshop práctico de GISELA

**Contenido y estado de ejecución:**

| Archivo | Para qué sirve | Ejecución |
|---|---|---|
| `WORKSHOP_TEGULARIS.md` | Guía de prácticas breves | Documentación |
| `01_cartas_gisela_v15.package.json` | Cinco fichas, 32 cartas, Slash/Double Slash/Blai del caballero con tiradas y TP | **Admitido y ejecutado en GISELA 0.1.21** |
| `02_diseno_productivo_completo.json` | Reglas y cartas del encuentro íntegro acordado | **Diseño: no es un paquete GISELA válido** |
| `03_simulador_escenario.py` y `simulador_base.py` | Banco de pruebas de balance, con Pride y explosión final; opción de jugar como Parnecio | Python independiente; **no ejecuta GISELA** |
| `04_contratos_pendientes.md` | Especificación de ampliaciones desacopladas al motor | Documentación técnica |
| `test_practica_nativa.py` | Pruebas del paquete nativo: admisión, propiedad, costo, restauración, determinismo | Python + GISELA 0.1.21 |

**Importante:** la carta *Protección* y las habilidades NPC están catalogadas pero no se ejecutan como combate real en la práctica nativa. Las pasivas permanecen en reserva para que no aparezcan como acciones voluntarias. Las extensiones generales del DSL son condición para ejecutar el encuentro completo de forma nativa.

## Inicio rápido

```bash
# En un entorno donde GISELA 0.1.21 está instalado
gisela validate 01_cartas_gisela_v15.package.json
glauquir --developer --package 01_cartas_gisela_v15.package.json
python 03_simulador_escenario.py --test
python 03_simulador_escenario.py --play --seed 20261103
```

Para ejecutar el test nativo, ejecute `python test_practica_nativa.py` en un entorno donde el paquete `gisela` esté en PYTHONPATH.

El origen técnico de este workshop es el archivo del repositorio GISELA 0.1.21 proporcionado por el autor. No se han modificado sus fuentes.
