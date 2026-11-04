# Resultados de integración y comprobación v0.7.7

**Base:** paquete v0.7.6 suministrado; nuevo paquete 09 generado sin alterar reglas de motor especializadas.

## Pruebas

- `python tools/check_quality.py`: **OK**, máximos 700/64/3.
- Regresión completa después de la incorporación del historial causal: **661 aprobadas, una omitida y 120 subpruebas aprobadas**, en 61,21 s. La prueba omitida depende de un paquete productivo externo no instalado.
- Tras ampliar el registro público autoral a 72 variables, la regresión dirigida de cierre + Observe/Act + DICE: **17 aprobadas**.
- Las siete pruebas focalizadas nuevas comprueban Bless, redirección grupal, explosión, prioridad de Groupal Shield, supresión de parálisis del protegido, integridad Observe/Act y restauración.

## Partidas ordinarias por Observe/Act

| Semilla hexadecimal | Política de Parnecio | Resultado | Acciones | Ronda |
|---|---|---|---:|---:|
| `00...00` | Ataque | Victoria | 75 | 6 |
| `00...00` | Pasar | Victoria | 148 | 12 |
| `00...01` | Protección | Victoria | 85 | 7 |

Las tres partidas se ejecutaron sin editar HP, MP, efectos ni RNG. Los recorridos verificaron la persistencia en el punto 13, y no hubo rechazo de acciones habilitadas. No se demostró derrota ni destrucción mutua mediante juego ordinario con estas semillas. Los tests de v0.7.2 siguen cubriendo esos dos desenlaces con estados preparados.

## Evidencia

- `EVIDENCIA_CAUSAL_V077.json`: una vista pública obtenida tras seis acciones con semilla `aa...aa`, incluidos hechos, dados y concursos confirmados.
- `tools/tegularis_campaign_v077.py`: recorrido reproducible sin modificación de estado interno.

## Deuda técnica

- La búsqueda exhaustiva de semillas para demostrar derrota y destrucción mutua no está cerrada. El balance debe examinarse antes de asegurar que ambos son alcanzables naturalmente.
- No se ha demostrado una redirección de daño individual a un aliado porque el catálogo actual no contiene una ruta de ataque individual contra él.
- Redondeo de 50 %: piso provisional.
- El historial causal se proyecta en ventana de 40 hechos; el completo se mantiene en la sesión persistida.
