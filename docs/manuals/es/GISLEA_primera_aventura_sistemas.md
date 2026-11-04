[Volver al inicio del tutorial](GISLEA_primera_aventura_narrativa.md).

# 3.6. La ficha de personaje: atributos, rasgos y azar

Quienes hayan jugado alguna vez un juego de rol de mesa probablemente recordarán las fichas de personaje, donde se anotan características como fuerza, inteligencia, habilidades y rasgos especiales. GISELA utiliza una idea parecida: una carta describe al personaje y sus características, mientras que el motor puede consultar sus valores y utilizarlos al resolver acontecimientos.

Vamos a utilizar la ficha de Tomás para comprobar si consigue recordar un detalle del paraguas.

Esta es una representación legible de los datos que hemos declarado para el personaje:

**FICHA DE PERSONAJE — TOMÁS**

| S.O.F.I.A. — Atributos | Valor |  
|---|---:|  
| Fuerza (`strength`) | 4 |  
| Apertura (`openness`) | 5 |  
| Fortuna (`fortune`) | 5 |  
| Inteligencia (`intelligence`) | 6 |  
| Percepción (`awareness`) | 5 |

**TRAITS — Rasgos**

*Atento a los detalles:* aporta +2 a las evaluaciones declaradas con el contexto `recuerdo`, cuando Tomás participa como actor.

**Prueba que realizaremos:** recordar un detalle del paraguas.

En el paquete, los atributos y la asignación del rasgo se declaran en la carta mediante las claves `sofia` y `traits`. Los valores numéricos pertenecen a S.O.F.I.A., mientras que el comportamiento del rasgo se define por separado en el catálogo de TRAITS.

La carta no ordena a Tomás recordar nada. Solamente proporciona características que podrán intervenir si una regla narrativa las utiliza.

* * *

Al igual que las fichas de los juegos de rol de mesa, S.O.F.I.A. permite representar características de los personajes mediante valores numéricos. El significado práctico de estos valores depende de las reglas que el autor establezca para su historia.

Por ejemplo, `awareness` puede representar la percepción de fenómenos sobrenaturales en un relato de misterio, la capacidad para advertir detalles del entorno en una investigación o un atributo que interviene en el uso de armas a distancia en una historia de aventuras.

Los atributos no ejecutan acciones por sí mismos: proporcionan valores que las reglas pueden consultar y utilizar. En nuestro ejercicio emplearemos `intelligence` para evaluar el recuerdo de Tomás, pero esta es una decisión de diseño de *El paraguas olvidado*, no una exigencia de GISELA.

La ficha describe las características del personaje; las reglas determinan cuándo y cómo intervienen en los acontecimientos.

Por ahora utilizaremos su valor efectivo, que en esta situación es 6.

* * *

Tomás posee el rasgo `atento_a_detalles`, pero tenerlo no significa que reciba +2 en todas las actividades.

El autor declaró que ese rasgo aporta una bonificación cuando la evaluación corresponde al contexto `recuerdo` y Tomás participa como actor.

Por ejemplo, ese mismo rasgo no tiene por qué ayudarlo a levantar un objeto pesado ni a convencer a otra persona. TRAITS solamente interviene cuando se cumplen las condiciones declaradas para su contribución.

En nuestra prueba, la bonificación es +2.

* * *

Elena le pregunta a Tomás si recuerda alguna característica que permita distinguir el paraguas. Él intenta hacer memoria, pero no sabemos si conseguirá recordar algo útil.

Utilizaremos una tirada de un dado de seis caras, representado como `1d6`. El motor combina los valores mediante esta fórmula declarada para la evaluación:

**Resultado = Inteligencia + Rasgo + Dado − Dificultad**

| Elemento | Valor |  
|---|---:|  
| Inteligencia efectiva | 6 |  
| Rasgo aplicable | +2 |  
| Dado | 1d6 |  
| Dificultad | −6 |  
| **Umbral para recordar** | **7** |

Si el dado arroja 4, el resultado será 6 y Tomás no conseguirá recordar. Si arroja 5, el resultado será 7 y recordará el detalle.

En este ejemplo, los resultados favorables del dado son 5 y 6: dos de sus seis caras. La probabilidad de éxito es, por tanto, de un tercio.

No se trata de una regla universal de GISELA. El autor ha definido los atributos utilizados, el dado, la dificultad y los resultados posibles para esta situación.

* * *

Ejecute el paquete de la quinta etapa en modo desarrollador:

```bash  
glauquir --developer --package paraguas_olvidado_etapa_5_ficha.package.json  
```

En la estación, examine el paraguas, comunique la contradicción a Tomás y pídale que recuerde algún otro detalle.

GLAUQUIR mostrará la evaluación y permitirá continuar según su resultado.

También puede consultar la ficha numérica del personaje mediante:

```text  
consultar scoresheet tomas  
```

Esta consulta permite inspeccionar los atributos de S.O.F.I.A. durante la partida. Es diferente de la carta de presentación que ve normalmente el jugador.

Para repetir una prueba con el mismo resultado, inicie GLAUQUIR utilizando una semilla fija mediante `--seed`. Si utiliza semillas diferentes, DICE puede producir resultados distintos, aunque los atributos y rasgos del personaje no hayan cambiado.

* * *

La ficha de Tomás nos ha permitido comprender tres funciones complementarias: S.O.F.I.A. aporta valores numéricos del personaje, TRAITS contribuye según las circunstancias declaradas y DICE resuelve una evaluación matemática que puede incorporar azar.

Ninguno de estos componentes decide por sí solo cómo continúa el relato. El autor ha preparado dos consecuencias: Tomás recuerda un detalle adicional o reconoce que no consigue hacerlo. GISELA ejecuta la consecuencia correspondiente al resultado.

En ambos casos, Elena podrá continuar y entregar el paraguas. Una tirada desfavorable no debe impedir que la historia termine, salvo que esa posibilidad de bloqueo sea deliberada y esté justificada por el diseño narrativo.

**Compruebe su historia:** repita la prueba con semillas diferentes, observe los resultados y verifique que tanto el éxito como el fracaso permiten alcanzar un desenlace.

# 3.7. Objetivos y misiones con MARY

Nuestra historia ya tiene personajes, decisiones, conocimientos, relaciones y una situación que puede resolverse mediante DICE. Solo nos falta una herramienta que permita seguir el propósito de Elena durante la partida: decidir qué hacer con el paraguas.

Para ello utilizaremos MARY, el componente de GISELA encargado de administrar objetivos y misiones.

Un **objetivo** representa algo que debe conseguirse o una condición que debe cumplirse. Una **misión** permite reunir uno o varios objetivos y seguir su progreso.

En *El paraguas olvidado* declararemos una misión llamada *El destino del paraguas*, con un único objetivo: decidir qué hacer con el objeto.

No necesitamos añadir puntos, premios ni tareas secundarias. La misión solamente nos permitirá comprobar que Elena ha resuelto la situación.

* * *

MARY utiliza condiciones para determinar cuándo se cumple un objetivo. En este caso comprobaremos si la historia contiene el hecho `paraguas_entregado`.

```json  
{  
  "id": "resolver_destino",  
  "mode": "milestone",  
  "visibility": "public",  
  "title": "Decidir qué hacer con el paraguas",  
  "criterion": {  
    "kind": "condition",  
    "when": {  
      "has_fact": "paraguas_entregado"  
    }  
  }  
}  
```

El modo `milestone` indica que estamos siguiendo un hito: una vez conseguido, permanece completado. Por su parte, `visibility: "public"` permite que el cliente muestre el objetivo al jugador.

Este fragmento forma parte de la sección `mary` del paquete. Allí también declaramos la misión que contiene el objetivo.

* * *

En nuestra primera implementación cometimos un error: registrábamos `paraguas_entregado` cuando Elena comenzaba a examinar el objeto, aunque todavía no había decidido entregarlo.

MARY interpretaba correctamente el hecho y completaba el objetivo, pero el guion había registrado un acontecimiento que aún no sucedía.

La corrección consistió en trasladar ese efecto al momento de la entrega.

Esto ilustra una regla importante: **los objetivos se evalúan a partir del estado narrativo; si los acontecimientos están mal registrados, el resultado también será incorrecto**.

* * *

Abra la versión completa del ejercicio:

```bash  
glauquir --package paraguas_olvidado_etapa_6_ficha.package.json  
```

Durante la partida escriba:

```text  
misiones  
```

Antes de entregar el paraguas, GLAUQUIR mostrará la misión activa y su objetivo pendiente. Puede examinar el objeto, conversar con Tomás y pedirle que recuerde otro detalle: la misión seguirá pendiente.

Cuando Elena entregue el paraguas, el objetivo se completará y la misión cambiará a `completed`.

Repita el ejercicio mediante la entrega directa. Aunque esta vez Elena no haya investigado, la misión también deberá completarse, porque su objetivo es resolver el destino del paraguas, no descubrir necesariamente quién es su propietario.

* * *

MARY permite seguir el progreso de una historia mediante objetivos definidos por el autor. Estos pueden depender de acontecimientos y condiciones, sin que sea necesario presentar una recompensa numérica al jugador.

En nuestro ejemplo, MARY no decide qué debe hacer Elena ni modifica las creencias de Tomás. Solamente comprueba cuándo se cumple el objetivo declarado.

Con esto hemos terminado la construcción de *El paraguas olvidado*. El paquete utiliza escenas, acontecimientos, decisiones, hechos, conocimientos, creencias, relaciones, atributos, rasgos, evaluaciones probabilísticas y seguimiento de objetivos.

**Compruebe su historia:** ejecute los dos desenlaces y verifique que la misión termina completada en ambos. Observe también que permanece pendiente mientras Elena investiga.

En el último apartado del workshop aprenderemos a comprobar la historia completa, identificar errores y reproducir los resultados de DICE.

# 3.8. Comprobar y depurar nuestra historia

Hemos terminado de construir *El paraguas olvidado*, pero todavía necesitamos comprobar que funciona como esperábamos. Una historia puede ejecutarse sin errores técnicos y, aun así, contener problemas narrativos: un personaje podría conocer información que nunca recibió, una conversación podría modificar la relación equivocada o una misión podría completarse antes de tiempo.

GLAUQUIR nos permite investigar estos problemas sin modificar el guion durante la partida.

Abra la versión completa del paquete en modo desarrollador:

```bash  
glauquir --developer --package paraguas_olvidado_etapa_6_ficha.package.json  
```

Recorra la historia siguiendo estas alternativas:

| Recorrido | Resultado esperado |  
|---|---|  
| Entregar directamente | Final `decision_incierta` |  
| Examinar y guardar silencio | Final `decision_informada` |  
| Examinar, comunicar la contradicción y entregar | Final `decision_informada` |  
| Examinar, comunicar y pedir otro detalle | Final `decision_informada`, con resultado variable de DICE |

Observe que tenemos dos finales, pero cuatro recorridos de prueba. Esto es normal: distintas decisiones pueden conducir a un mismo desenlace conservando consecuencias diferentes.

* * *

Durante una partida iniciada con `--developer`, puede escribir:

```text  
hechos  
```

GLAUQUIR mostrará los hechos registrados. Si Elena examinó el paraguas, debería encontrar `etiqueta_descubierta`. Si lo entregó directamente, ese hecho no debería aparecer.

También puede consultar el estado de Tomás:

```text  
consultar personaje tomas  
```

Esta consulta permite examinar sus conocimientos y creencias. Si Elena guardó silencio, Tomás debe conservar su creencia inicial sobre el paraguas; si le comunicó la contradicción, la creencia debe haber cambiado.

Para comprobar su confianza hacia Elena, utilice:

```text  
relacion tomas elena confianza  
```

El resultado esperado después de comunicar la contradicción es 1. Si Elena no la comunicó, debe permanecer en su valor inicial de 0.

Para consultar los atributos de la ficha de Tomás:

```text  
consultar scoresheet tomas  
```

Recuerde que estos comandos son herramientas de diagnóstico. En una sesión normal, GLAUQUIR no revela indiscriminadamente la información privada de los personajes.

* * *

Durante la investigación, escriba:

```text  
misiones  
```

La misión *El destino del paraguas* debe encontrarse activa mientras Elena todavía no haya entregado el objeto.

Cuando ocurre la entrega, MARY debe marcar el objetivo como completado. La misión y el final son cosas distintas: ambos desenlaces cumplen el objetivo, aunque Elena llegue a ellos con diferente información.

* * *

Una propiedad importante de GISELA es que sus evaluaciones probabilísticas son reproducibles. Si repetimos una partida desde el mismo estado, con las mismas decisiones y el mismo estado del generador aleatorio, obtendremos el mismo resultado.

Podemos comprobarlo sin conocer el funcionamiento interno de DICE.

Antes de seleccionar «Pedir más detalles», guarde la partida:

```text  
guardar antes_del_recuerdo.json  
```

Después realice la evaluación y observe si Tomás consiguió recordar.

Mientras la sesión siga abierta, restaure el estado guardado:

```text  
cargar antes_del_recuerdo.json  
```

Repita la misma acción. El resultado debe coincidir con el anterior.

Guardar una partida conserva también la información necesaria para continuar las evaluaciones probabilísticas de manera reproducible. No debemos confundir esta propiedad con que todos los jugadores tengan que obtener siempre el mismo resultado: distintas sesiones iniciales pueden utilizar semillas diferentes.

* * *

Al revisar una historia, conviene formular preguntas concretas.

¿Un personaje sabe algo que todavía no debería conocer? Revise los efectos que entregan conocimiento.

¿Una acción puede ejecutarse varias veces y producir la misma recompensa? Compruebe sus condiciones y los hechos que registran su ejecución.

¿Una misión se completa demasiado pronto? Verifique cuándo se registra el acontecimiento utilizado como criterio.

¿Una tirada desfavorable impide terminar el relato? Compruebe que exista una salida narrativa válida para ese resultado.

La validación del paquete y estas comprobaciones cumplen funciones complementarias. La primera examina si las declaraciones cumplen los contratos de GISELA; las segundas permiten determinar si la historia se comporta como pretendía su autor.

* * *

A partir de una situación sencilla, construimos un guion productivo con personajes, escenas, objetos, acciones, hechos, conocimientos, creencias, relaciones dirigidas, atributos, rasgos, evaluaciones probabilísticas, objetivos y finales.

No fue necesario programar cada situación en Python. Declaramos sus posibilidades mediante el DSL y dejamos que GISELA ejecutara las reglas correspondientes.

**El siguiente paso es construir su propia historia.** Puede comenzar con dos personajes, un conflicto y un par de decisiones, y agregar nuevos mecanismos solamente cuando el relato los necesite. No hace falta utilizar todas las capacidades del motor para producir una historia interactiva completa.


