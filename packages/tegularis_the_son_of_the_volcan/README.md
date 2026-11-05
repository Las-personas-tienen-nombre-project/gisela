# Tegularis: Taller práctico de GISELA

Este directorio conserva una secuencia de prácticas y ampliaciones. La
práctica inicial del paquete 01 tiene un alcance reducido; el paquete
`09_cierre_autoral_v077.package.json` ejecuta el combate completo mediante
Observe/Act y GLAUQUIR. Comience por el [taller de cierre](WORKSHOP_CIERRE_V077.md)
si quiere recorrer ese encuentro. Los límites de las guías iniciales se
conservan como antecedentes de cada etapa.

**Contenido y estado de ejecución:**

| Archivo | Para qué sirve | Ejecución |
|---|---|---|
| `WORKSHOP_TEGULARIS.md` | Guía de prácticas breves | Documentación |
| `01_cartas_gisela_v15.package.json` | Cinco fichas, 32 cartas, Slash/Double Slash/Blai del caballero con tiradas y TP | **Admitido y ejecutado en GISELA 0.1.21** |
| `02_diseno_productivo_completo.json` | Reglas y cartas del encuentro íntegro acordado | **Diseño: no es un paquete GISELA válido** |
| `03_simulador_escenario.py` y `simulador_base.py` | Banco de pruebas de balance, con Pride y explosión final; opción de jugar como Parnecio | Python independiente; **no ejecuta GISELA** |
| `04_contratos_pendientes.md` | Especificación de ampliaciones desacopladas al motor | Documentación técnica |
| `test_practica_nativa.py` | Pruebas del paquete nativo: admisión, propiedad, costo, restauración, determinismo | Python + GISELA 0.1.21 |

**Límite de la práctica inicial:** en el paquete 01, *Protección* y las habilidades de NPC están catalogadas, pero no forman un combate completo. Las pasivas permanecen en reserva para que no aparezcan como acciones voluntarias. Esta restricción de la práctica inicial no se aplica al paquete 09.

## Inicio rápido

```bash
# En un entorno donde GISELA 0.1.21 está instalado
gisela validate 01_cartas_gisela_v15.package.json
glauquir --developer --package 01_cartas_gisela_v15.package.json
python 03_simulador_escenario.py --test
python 03_simulador_escenario.py --play --seed 20261103
```

Para ejecutar el test nativo, ejecute `python test_practica_nativa.py` en un entorno donde el paquete `gisela` esté en PYTHONPATH.

El origen técnico de este taller es el archivo del repositorio GISELA 0.1.21 proporcionado por el autor. No se han modificado sus fuentes.
