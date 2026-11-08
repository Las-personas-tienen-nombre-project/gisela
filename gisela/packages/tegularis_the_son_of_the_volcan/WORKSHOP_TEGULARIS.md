# GISELA: Taller 2: Tegularis, el Hijo del Volcán

**Alcance histórico:** esta guía describe la práctica inicial del archivo
`01_cartas_gisela_v15.package.json`. Sus limitaciones no representan
las capacidades actuales del motor. El [taller de cierre](WORKSHOP_CIERRE_V077.md)
utiliza el combate completo del paquete 09; los
[talleres de presentación](../../../docs/history/workshops/presentacion/README.md) explican las vistas posteriores.

**Laboratorio práctico de cartas, TRAITS, S.O.F.I.A. y DICE**  
**Jugador:** Parnecio Esparcales; **Compañeros:** Gillius Cabezadeencina, Clarisa de la Hojarasca e Iosepus Knechti.

**Enemigo:** Tegularis, el Hijo del Volcán.

> **Alcance comprobado (GISELA 0.1.21, DSL 1.5).** Este material contiene una práctica **ejecutable en GISELA** para crear fichas y probar las habilidades ofensivas de Parnecio, y un **diseño completo del encuentro** acompañado por un simulador independiente. Todavía **no** contiene un combate íntegro ejecutable en GISELA: faltan operaciones generales, especialmente la invocación de habilidades de NPC y las habilidades parametrizadas. El simulador NO es GISELA y no sustituye su motor. Separamos las partes para que la guía no enseñe instrucciones que el motor rechace.

## Práctica 1: Abrir y comprobar las cinco fichas (5 minutos)

1. Instale la versión del repositorio de GISELA 0.1.21 en un entorno Python, siguiendo su README.
2. Coloque `01_cartas_gisela_v15.package.json` en una carpeta de trabajo.
3. Valide el paquete:

```bash
gisela validate 01_cartas_gisela_v15.package.json
```

4. Abra el escenario:

```bash
glauquir --developer --package 01_cartas_gisela_v15.package.json
```

5. En la consola, consulte las fichas:

```text
consultar scoresheet parnecio
consultar scoresheet gillius
consultar scoresheet clarisa
consultar scoresheet iosepus
consultar scoresheet tegularis
```

En el primer nodo se resuelve también una **evaluación DICE real** de esquiva: GISELA lee Awareness de Parnecio y TRAITS aporta +2 por Dodge en el contexto `evasion`. Con una semilla fija, puede consultar `hechos` y comparar si se registró `esquiva_entrenamiento`. La carta pasiva todavía no concede automáticamente el TRAIT: el personaje lo posee como parte de su ficha inicial.

**Compruebe:** Parnecio (S8/O5/F6/I4/A6); Gillius (10/4/5/4/5); Clarisa (4/7/9/7/7); Iosepus (4/5/6/9/8); Tegularis (15/7/5/9/7). La escala S.O.F.I.A. de este juego va de 0 a 20: no es una escala impuesta a otros autores.

## Práctica 2: Cartas propias y habilidades jugables (5 minutos)

En la primera ventana de habilidades, observe que Parnecio tiene **Slash**, **Double Slash** y **Blai**. Double Slash y Blai aparecen inicialmente deshabilitadas porque Parnecio comienza con cero TP.

1. Juegue **Slash**. La carta ejecuta sus tiradas, añade el daño si acierta y concede 10 TP.
2. En la ventana siguiente, juegue **Double Slash**. La carta consume 10 TP y resuelve dos intentos independientes de impacto.
3. Reinicie la partida. Esta vez juegue **Slash** tres veces y después **Blai**: habrá acumulado 30 TP y podrá gastar esa cantidad en la estocada.
4. Para comprobar la repetibilidad, abra GLAUQUIR con una semilla fija y repita las mismas elecciones:

```bash
glauquir --developer --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --package 01_cartas_gisela_v15.package.json
```

**Compruebe:** una habilidad no ejecutable no se ofrece como acción habilitada; las cartas usadas retornan a la mano, los TP cambian según la carta y una semilla idéntica reproduce las tiradas cuando se conserva la secuencia de acciones.

**Límite intencionado de esta práctica:** la evasión del dragón está fijada a 6 en esta vertical, que es el valor inicial derivado de sus atributos y del rasgo *Enorme*. No implementamos aquí su recomputación dinámica ante modificadores ni una batalla con NPC. **Protección** y las pasivas están catalogadas en reserva y todavía no ejecutan sus efectos de combate.

## Práctica 3: Leer las reglas declaradas (5 minutos)

Abra `02_diseno_productivo_completo.json`. Es el **documento de diseño**, no un paquete aceptado por el validador de GISELA. Localice `participants`, `initiative`, `actions`, `combat`, `skills`, `pride` y `death_burst`.

Compruebe que la iniciativa está definida por el autor como `STR + AWA + FOR + 1d10`; las acciones derivan del atributo principal y TRAITS, con umbrales 7 y 10; el Hit Roll usa Awareness y el Evasion Roll combina Strength con Awareness. El Damage Roll usa el atributo declarado en cada carta, salvo que la habilidad defina una fórmula propia.

Los recursos iniciales del encuentro son: aventureros, `HP = 150 + STR + 1d20`, `MP = 50 + INT + 1d10`, `TP = 0/50`; Tegularis, `HP = 500 + 3d20`, `MP = 80 + 1d20`, `TP = 50/60`. Las cantidades y dados de bonificación siguen siendo **parámetros de equilibrio propuestos**, mientras que las bases y el TP inicial del dragón son decisiones acordadas.

## Práctica 4: Las decisiones de los compañeros (5 minutos)

Lea las cartas de habilidades en la clave `skills` y compruebe estas reglas de actuación del autor:

**Clarisa** prioriza supervivencia propia, curación urgente de aliados con HP <=25 %, Fénix para los caídos, Groupal Shield durante Onslaught o ante una amenaza anticipada, protección de aliados, Bless cuando todos superan 60 % en Recovery, Regeneración y Curación. Si no puede ejecutar una habilidad, considera la siguiente; si necesita maná, utiliza Concentración. *El costo de Bless sigue por definir.*

**Gillius** combate agresivamente: adopta Stance Aggressive, usa Grito de guerra cuando corresponde, Eviscerate al reunir TP y Hachazo para seguir atacando y acumular TP. Dodge y la postura contribuyen al Evasion Roll mediante TRAITS.

**Iosepus** procura conservar maná, intenta debilitar a Tegularis con Agarraguirre, protege con Armadura mágica, potencia a un aliado con Firesteel y ataca con Magic Blast. Este último recibe el parámetro `x` del guion: paga `1 + x` de maná, obtiene `floor(x/10)` al Hit Roll y suma `x` al daño basado en Intelligence.

**Tegularis** busca destruir al grupo tan pronto como pueda. Utiliza sus ataques de área y técnicas físicas antes de depender de Preponderancia de la leyenda. Esa carta consume una acción, recupera 8 TP y 8 MP y aplica **Protegido** (-5 a todo daño) hasta el comienzo de su siguiente turno; no acumula la protección consigo misma.

**Tarea:** cambie el orden de dos prioridades en una copia del documento de diseño y explique qué efecto debería tener sobre la próxima acción del NPC. No modifica GISELA hasta que exista la operación declarativa general `play(skill)` para NPC.

## Práctica 5: Ejecutar el banco de pruebas del encuentro (5 a 10 minutos)

El archivo `03_simulador_escenario.py` es un banco de pruebas Python **independiente de GISELA** para detectar problemas de equilibrio. Utiliza `simulador_base.py` y no genera un paquete narrativo.

Pruebe sus invariantes:

```bash
python 03_simulador_escenario.py --test
```

Ejecute 500 combates reproducibles:

```bash
python 03_simulador_escenario.py --runs 500 --seed 20261103
```

Revise una partida completa:

```bash
python 03_simulador_escenario.py --trace --seed 20261103
```

O pruebe las decisiones de Parnecio desde la terminal:

```bash
python 03_simulador_escenario.py --play --seed 20261103
```

**Compruebe:** el dragón comienza con 50 TP; Pride of the Volcan Son se activa una sola vez cuando queda vivo con <=30 % de HP; el +1 afecta sus cinco atributos; y al caer a cero se ejecuta automáticamente **"Si vas a perder asegurate de que no ganan por mucho"**. La explosión causa `30 + INT efectivo + 1d10` a todo el grupo, sin Hit ni Evasion Roll, pero respetando las protecciones. Puede producir destrucción mutua.

**Advertencia:** este simulador es aproximado. Algunas prioridades y valores no cerrados se representan con supuestos. Úselo para explorar, **no** para afirmar que GISELA ya soporta esa partida.

## Práctica 6: Qué debe resolver la ampliación general de GISELA

Abra `04_contratos_pendientes.md`. Los cambios necesarios son **primitivas generales**, no reglas codificadas para combates: ejecución de habilidades de cualquier propietario bajo autoridad del guion; parámetros tipados en una invocación; expresiones declarativas compuestas; acontecimientos definidos por el autor; ciclo de vida de TRAITS ligados a cartas o efectos; y una forma de expresar una ejecución disparada al morir que se resuelva antes del final.

No acepte una ampliación por el solo hecho de que *funcione con Tegularis*. Debe superar también los casos de transacción rechazada, reproducción por semilla, restauración y ausencia de control del jugador sobre las habilidades de los NPC.

### Lista de comprobación final

- [ ] Se admiten las cinco fichas y se conservan sus valores.
- [ ] Slash genera TP y Double Slash/Blai comprueban sus costos.
- [ ] El jugador no puede usar una habilidad perteneciente a Tegularis.
- [ ] Los TRAITS provienen del personaje, carta o efecto correcto y no se duplican sin autorización.
- [ ] La estrategia de Clarisa y de Iosepus se expresa en el guion, no en el motor.
- [ ] Preponderancia, Pride y la explosión final se resuelven exactamente una vez cuando corresponde.
- [ ] La derrota de Tegularis no confirma el desenlace antes de la explosión.

**Resultado de este material:** práctica nativa reproducible para cartas del caballero, especificación completa del sistema del autor y pruebas de diseño preparadas para guiar las extensiones de GISELA. No equivale todavía a un paquete productivo íntegro del combate.
