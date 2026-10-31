> **Actualización posterior (E2, ADR-022):** las limitaciones de ejecución v1.4 descritas a continuación corresponden al cierre histórico E1. El runtime E2 ejecuta evaluaciones ocultas y admite guardados v1.4; las evaluaciones visibles y reconocidas siguen pendientes.

# E1: Contrato declarativo y normalizador de GISELA v1.4

**Implementado:** validación de autoría y compilación pura. **No ejecutable:** el motor rechaza sesiones de un paquete v1.4 hasta E2.

## Ejemplo de autoría

El siguiente fragmento es un **paso de nodo**, no una operación ni un programa de DICE. El paquete debe declarar `facts` si usa `record_fact` y la tabla `dice_profiles`:

```json
{
  "dice_profiles": [
    {"schema_version":"dice.profile.v1","id":"repair_check","mode":"dice_sum",
     "count":2,"sides":6,"bands":[{"id":"blocked","min":0},{"id":"complete","min":10}]}
  ]
}
```

```json
{
  "id":"test_machine", "op":"evaluate",
  "evaluation": {
    "id":"attempt_repair", "profile":"repair_check", "presentation":"acknowledged",
    "inputs":{"base":{"stat":{"character":"technician","name":"intelligence","component":"effective"}},
              "difficulty":{"literal":5}},
    "context":{"participants":[{"entity":"technician","role":"actor"}], "tags":["repair"]},
    "branches":[
      {"outcome":"blocked", "effects":[]},
      {"outcome":"complete", "effects":[{"op":"record_fact","fact":"repair_completed"}]}
    ]
  }
}
```

El personaje `technician` debe existir como instancia declarada, su carta debe tener S.O.F.I.A. y, si posee rasgos activos, el paquete debe contener el catálogo TRAITS correspondiente. El ejemplo no se ejecuta aislado: faltan el resto de campos obligatorios del paquete.

Una historia sin S.O.F.I.A. ni TRAITS puede sustituir `base` por `{"literal":3}` y omitir `context`. La política de presentación no presupone un humano: quien solicita la acción, su identidad autorizada y la entidad narrativa son independientes.

## API de compilación offline

```python
from gisela.contracts.admit_package import admit_package
from gisela.contracts.evaluation_plan import compile_package_evaluations

admitted = admit_package(package)  # JSON Schema + referencias + ramas + presupuesto
compiled = compile_package_evaluations(admitted.materialize())
plan = compiled['/nodes/0/steps/0']
# plan['request'] contiene exactamente las claves que espera traits_dice_bridge.resolve()
# NO llamar todavía desde el ejecutor E1; esta es solo una verificación offline.
```

`plan` contiene `id`, `presentation`, `request` y `branches` indexadas por resultado. `request` contiene `profile` materializado, `base` entero, `difficulty` entero, `participants` explícitos, `tags` explícitos y, opcionalmente, referencia `stat` para lectura *en el momento de la ejecución E2*. El contrato neutral que verá DICE continúa siendo `{base,bonus,difficulty}`: GISELA compone el `bonus` de TRAITS y la base de S.O.F.I.A. mediante el adaptador preexistente. Ningún estado compartido, ni función de RNG, atraviesa la frontera de admisión.

Los cambios de estado deben producirse únicamente en GISELA mediante las consecuencias declaradas. La compilación no confirma selecciones, tiempos, eventos, reacciones o MARY. `presentation` no autoriza divulgar modificadores secretos: la política pública se definirá en E3 con la audiencia E0.

## Exclusiones y compatibilidad

- `evaluate` como paso es **observable** por diseño, nunca un `effect` automático; E2 debe ofrecerlo correctamente.
- Opciones y acciones que definen `evaluation` **no pueden** tener sus propios `effects`/`next` inmediatos.
- Reacciones, habilidades, `on_apply`, `on_expire`, cierre e inicio de nodos no admiten estas evaluaciones visibles.
- Los archivos v1.2 y v1.3, RNG y núcleos independientes DICE/TRAITS no se modifican.
- `Validator.validate_session()` rechaza v1.4 hasta que exista un contrato de guardado realmente ejecutable. Nunca se fabrican snapshots v1.4 por reinterpretación de v1.3.

**Debilidad conocida y documentada:** E1 todavía no puede probar el rango efectivo de la suma TRAITS/S.O.F.I.A. para una entidad mutable. E2 debe validar la solicitud neutral compuesta **antes del primer sorteo**, y revalidar la disponibilidad de entidades/rangos al autorizar la acción.
