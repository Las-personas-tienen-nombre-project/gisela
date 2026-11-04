# Workshop — Tegularis: Pride, explosión y desenlaces (v0.7.2)

Desde la raíz de GISELA:

```bash
PYTHONPATH=. python gisela/packages/tegularis_the_son_of_the_volcan/build_v072.py
PYTHONPATH=. pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_desenlaces_v072.py
```

Paquete: `08_desenlaces_v072.package.json`.

1. Abra `actuation.event_policies` en el JSON. Identifique la fase `immediate` de Pride y la fase `after_action` de Última llama.
2. Compruebe que Pride exige HP positivo y ≤ 30 % del HP inicial. El efecto `ef_pride_volcan` otorga los cinco modificadores de S.O.F.I.A. y la reducción consultada por TRAITS.
3. Compruebe que la explosión usa la misma corriente de dados de GISELA, produce un aviso numérico y aplica las reducciones sin Hit/Evasion.
4. Active Groupal Shield; compruebe que se consume una vez y evita la explosión completa.
5. Fuerce por medio de las pruebas los tres desenlaces: victoria, derrota y destrucción mutua. Observe que el cierre ocurre **después** del daño final.
6. Compare el mismo guardado antes de la explosión al continuar por dos sesiones independientes: ambos estados deben coincidir exactamente.

Los siete tests automatizados cubren estos pasos. Los casos de HP forzado pertenecen a las pruebas de laboratorio, no a una interfaz pública de edición de estado.

### Pendientes explícitos

Protección y Bless siguen sin contrato cerrado. La integración con Observe/Act y GLAUQUIR productivo corresponde a v0.7.3. La regresión general no ha terminado en esta entrega.
