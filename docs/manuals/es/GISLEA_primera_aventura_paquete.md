[Volver al inicio del tutorial](GISLEA_primera_aventura_narrativa.md).

# 3.1. Del relato al guion productivo

Nuestra historia comienza una tarde lluviosa, en una estación de tren. Elena encuentra un paraguas azul cerca de una banca y Tomás, otro pasajero, asegura haber visto a una compañera de trabajo dejarlo allí. Sin embargo, Elena puede descubrir una etiqueta cuyas iniciales no coinciden con las de esa persona.

No sabemos todavía quién es el propietario. Tampoco podemos concluir que Tomás esté mintiendo: podría haber confundido dos paraguas.

Antes de escribir las declaraciones de GISELA, identificaremos los elementos indispensables de la historia.

| Elemento | Declaración que necesitaremos |  
|---|---|  
| Elena y Tomás | Dos personajes |  
| Estación de tren | Un escenario |  
| Paraguas azul | Un objeto |  
| Hallazgo y testimonio | Acontecimientos |  
| Examinar, conversar o entregar | Acciones |  
| Etiqueta descubierta | Hecho y conocimiento individual |  
| Creencia de Tomás | Estado individual |  
| Entrega del paraguas | Consecuencia |  
| Decisión informada o incierta | Dos finales |

Esta tabla es nuestra primera ficha de producción. Todavía no es código ni JSON: expresa qué necesita representar GISELA para ejecutar la historia.

Observe que hemos distinguido tres cosas. El paraguas tiene una etiqueta; Elena puede descubrirla; y Tomás puede desconocer ese descubrimiento. Una propiedad del objeto, el conocimiento de Elena y la creencia de Tomás son aspectos relacionados, pero no equivalentes.

También evitaremos que el azar decida todo. Elena podrá terminar la historia aunque una evaluación resulte desfavorable, porque la incertidumbre debe formar parte del relato y no convertirse en un impedimento accidental para concluirlo.

En los ejercicios siguientes convertiremos esta ficha en declaraciones del DSL, comenzando por el paquete narrativo más pequeño que pueda ejecutarse.

# 3.2. Crear y ejecutar el primer paquete

Ya conocemos la situación inicial de *El paraguas olvidado*: Elena encuentra un objeto, escucha el testimonio de Tomás y debe decidir qué hacer. Ahora vamos a convertir esa situación en una historia ejecutable.

Comenzaremos por una versión sencilla, con dos opciones y dos finales. Todavía no registraremos conocimientos ni relaciones entre personajes; esos mecanismos aparecerán cuando necesitemos que los acontecimientos tengan consecuencias sobre el estado de la historia.

Cree una carpeta llamada `el-paraguas-olvidado` dentro de su espacio de trabajo. En ella guardaremos los archivos del taller.

Abra su editor de texto y prepare un archivo llamado `paraguas_olvidado_etapa_1.package.json`. La extensión `.json` indica que su contenido está escrito en JSON; la parte `.package` forma parte de la convención que utilizaremos para identificar los paquetes de GISELA.

Un paquete contiene varias secciones. La primera es `manifest`, que identifica la historia y establece cómo debe comenzar.

```json  
{  
  "manifest": {  
    "id": "paraguas_olvidado_etapa_1",  
    "format_version": "1.5",  
    "language": "es_cl",  
    "languages": ["es_cl"],  
    "entry": {  
      "node": "inicio"  
    }  
  }  
}  
```

Este fragmento muestra solamente el manifiesto; todavía no constituye un paquete completo.

Observe especialmente dos declaraciones: `language` establece el idioma original de la historia y `entry` indica que la ejecución comenzará en el nodo llamado `inicio`.

Un **nodo** es una unidad del guion que contiene pasos narrativos. Podemos utilizarlo para presentar texto, ofrecer decisiones y conducir hacia otros nodos.

* * *

El nodo inicial contiene una descripción, el testimonio de Tomás y la decisión de Elena. Este es uno de sus pasos narrativos:

```json  
{  
  "id": "presentacion",  
  "op": "narrate",  
  "text": {  
    "text": "La lluvia golpeaba los vidrios de la estación. Elena esperaba el último tren cuando vio un paraguas azul abandonado junto a una banca."  
  }  
}  
```

La operación `narrate` le indica al motor que debe presentar un texto narrativo. El contenido está dentro de `text`, mientras que `id` permite identificar el paso dentro de su nodo.

Para incorporar una decisión utilizamos `choice`. Cada alternativa tiene una etiqueta visible y una referencia al nodo que continuará la historia.

```json  
{  
  "id": "decision",  
  "op": "choice",  
  "prompt": {  
    "text": "¿Qué hace Elena con el paraguas?"  
  },  
  "options": [  
    {  
      "id": "examinar",  
      "label": {  
        "text": "Examinar el paraguas antes de decidir"  
      },  
      "next": {  
        "node": "examina"  
      }  
    },  
    {  
      "id": "entregar",  
      "label": {  
        "text": "Llevarlo directamente a objetos perdidos"  
      },  
      "next": {  
        "node": "entrega"  
      }  
    }  
  ]  
}  
```

En nuestro primer paquete, `examina` y `entrega` son otros dos nodos. Cada uno contiene el texto correspondiente y termina con la operación `ending`.

Los identificadores `examina`, `entrega` y `inicio` son nombres que hemos elegido para esta historia. En cambio, `choice`, `options`, `next` y `node` forman parte del vocabulario del DSL y deben escribirse conforme a sus contratos.

* * *

El archivo completo de esta etapa acompaña al manual. Ábralo en su editor y busque las secciones `manifest`, `nodes` y `endings`; podrá reconocer las declaraciones que acabamos de estudiar.

Para comprobarlo, abra una terminal en la carpeta que contiene el archivo y ejecute, con los comandos de GISELA instalados:

```bash  
gisela validate paraguas_olvidado_etapa_1.package.json  
```

Si la validación resulta satisfactoria, inicie GLAUQUIR:

```bash  
glauquir --package paraguas_olvidado_etapa_1.package.json  
```

Si está utilizando el entorno virtual sin activarlo, ejecute estos programas mediante las rutas indicadas en la sección 2.

GLAUQUIR presentará el relato inicial y, al llegar a la decisión, ofrecerá las dos alternativas. Recorra primero la opción de examinar el paraguas y compruebe que la historia termina en `decision_informada`. Después inicie otra partida y entregue el objeto directamente; esta vez debe alcanzar `decision_incierta`.

* * *

Nuestra primera versión ya puede ejecutarse de principio a fin, pero su funcionamiento todavía es el de una narración ramificada sencilla. Elena descubre una etiqueta porque el nodo correspondiente contiene ese texto, no porque el motor haya registrado que ella adquirió un conocimiento nuevo.

Eso cambiará en el siguiente ejercicio. Incorporaremos una escena, los personajes y el paraguas como entidades del mundo, además de hechos que permitan conservar las consecuencias de lo ocurrido.

**Compruebe su historia:** ejecute las dos alternativas y verifique que cada una llega al final previsto. Si una opción no funciona, revise que el identificador de su nodo de destino coincida exactamente con el declarado en el paquete.

# 3.3. Dar estado a la historia

Nuestra primera versión de *El paraguas olvidado* ya tenía una escena inicial, una decisión y dos finales. Sin embargo, cuando Elena examinaba el paraguas, el descubrimiento de la etiqueta solamente aparecía en el texto. Si más adelante quisiéramos ofrecer una acción exclusiva para quienes conocen ese indicio, necesitaríamos que GISELA pudiera comprobar que el descubrimiento ocurrió.

Para conseguirlo incorporaremos dos elementos: **entidades**, que representan las cosas y personas de nuestra historia, y **hechos**, que permiten conservar información sobre los acontecimientos.

Elena y Tomás son personajes; el paraguas es un objeto y la estación es el lugar donde transcurre la historia. GISELA permite representar estos elementos mediante cartas y escenas.

Una carta describe una entidad de nuestra historia. Por ejemplo, podemos declarar el paraguas azul con un identificador, un título y una descripción. La escena establece qué personajes y elementos están presentes en el lugar que explora el jugador.

La versión 2 del paquete incorpora estas declaraciones. Al ejecutarla con GLAUQUIR, podemos reconocer la estación, sus personajes y el paraguas, sin necesidad de escribir instrucciones gráficas particulares para presentarlos.

Es importante distinguir **la definición de una entidad de su estado durante la partida**. La carta establece qué es el paraguas; el estado narrativo puede registrar qué ha sucedido con él. Que una carta exista no significa, por sí solo, que el jugador haya descubierto el objeto o que lo lleve consigo.

* * *

Cuando Elena examina el paraguas y descubre la etiqueta, queremos conservar ese descubrimiento. Para ello utilizaremos la operación `record_fact`:

```json  
{  
  "op": "record_fact",  
  "fact": "etiqueta_descubierta"  
}  
```

Esta declaración no presenta texto ni modifica automáticamente el conocimiento individual de Elena. Registra un hecho narrativo que otras condiciones y reglas pueden utilizar.

Durante la historia también registraremos que Elena encontró el paraguas, que lo examinó y que finalmente lo entregó. Cada identificador representa un acontecimiento diferente, aunque varios ocurran durante una misma secuencia narrativa.

* * *

Supongamos que queremos ofrecer la opción de examinar el paraguas solamente mientras Elena no lo haya examinado.

La condición correspondiente debe comprobar la ausencia del hecho `paraguas_examinado`. Una vez que la acción lo registre, la misma opción dejará de estar disponible.

No necesitamos escribir una segunda escena que diga «el paraguas ya fue examinado». Podemos utilizar el estado existente para determinar qué acciones corresponden.

Este es uno de los beneficios principales del guion declarativo: **las condiciones consultan lo ocurrido, mientras que los efectos registran sus consecuencias**.

* * *

Ejecute la segunda versión del paquete:

```bash  
glauquir --package paraguas_olvidado_etapa_2.package.json  
```

Recorra primero la alternativa de examinar el paraguas. Al terminar, el historial deberá contener los hechos `paraguas_encontrado`, `paraguas_examinado`, `etiqueta_descubierta` y `paraguas_entregado`.

Después inicie una partida nueva y entregue el paraguas sin examinarlo. En ese recorrido no deberían registrarse ni `paraguas_examinado` ni `etiqueta_descubierta`.

Puede consultar los hechos mediante el comando `hechos` de GLAUQUIR, en modo desarrollador.

* * *

Una historia puede narrar un acontecimiento y, además, conservar sus consecuencias como datos. Esto permite que decisiones posteriores dependan de lo ocurrido, sin tener que mantener una copia distinta del guion para cada combinación.

Por ahora, nuestros hechos pertenecen al registro general de la historia. Todavía no hemos representado qué sabe Elena sobre la etiqueta ni qué cree Tomás acerca de su propietario.

En el siguiente ejercicio utilizaremos ALBERTO para distinguir entre **lo que ocurrió en el mundo y la información que posee cada personaje**.

**Compruebe su historia:** compare los hechos registrados al terminar ambos recorridos. El descubrimiento de la etiqueta debe aparecer exclusivamente cuando Elena haya examinado el paraguas.

# 3.4. Lo que saben y creen los personajes

Hasta ahora hemos registrado acontecimientos que pertenecen a la historia: Elena encontró el paraguas, lo examinó y descubrió una etiqueta. Pero ¿qué ocurre si Tomás no estaba presente cuando ella hizo el descubrimiento? ¿Debería conocer también esa información?

No necesariamente. **Que algo haya sucedido no significa que todos los personajes lo sepan.** Para representar esta diferencia utilizaremos ALBERTO, el componente de GISELA que administra, entre otras cosas, los conocimientos, creencias y relaciones de los personajes.

Consideremos tres declaraciones relacionadas con el paraguas:

- **Hecho:** el paraguas tiene una etiqueta con determinadas iniciales.  
- **Conocimiento:** Elena descubrió la etiqueta al examinar el objeto.  
- **Creencia:** Tomás piensa que el paraguas pertenece a una compañera de trabajo.

Las tres pueden coexistir sin contradecirse. Tomás no tiene por qué conocer la etiqueta, y Elena puede escuchar su testimonio sin darlo por verdadero.

Esta distinción permite construir personajes que disponen de información diferente. También evita que una sospecha se convierta automáticamente en una verdad dentro de la historia.

* * *

Cuando Elena escucha el testimonio de Tomás, podemos registrar que recibió esa información mediante `learn_fact`:

```json  
{  
  "op": "learn_fact",  
  "character": "elena",  
  "fact": "tomas_declaracion_recibida"  
}  
```

Observe que identificamos expresamente al personaje que adquiere el conocimiento. No estamos indicando que la declaración de Tomás sea verdadera, sino que Elena conoce lo que él dijo.

Si más adelante Elena descubre la etiqueta, podremos registrar ese segundo conocimiento sin modificar automáticamente el de Tomás.

* * *

Al comenzar nuestra historia, Tomás cree reconocer el paraguas. Podemos representar esa interpretación mediante una creencia de su personaje:

```json  
{  
  "beliefs": {  
    "paraguas_es_de_companera": true  
  }  
}  
```

Este fragmento pertenece al estado inicial de Tomás en el paquete completo. El valor `true` indica que sostiene esa creencia; no demuestra que el paraguas pertenezca efectivamente a su compañera.

Si Elena obtiene información contradictoria, la creencia de Tomás permanece intacta mientras él no reciba antecedentes o experimente un acontecimiento que justifique revisarla.

Más adelante utilizaremos `set_belief` para mostrar cómo puede cambiar de opinión.

* * *

Abra la tercera versión del paquete:

```bash  
glauquir --developer --package paraguas_olvidado_etapa_3.package.json  
```

Recorra primero la alternativa en que Elena examina el paraguas. Después consulte los hechos y conocimientos disponibles mediante las herramientas de diagnóstico de GLAUQUIR.

Elena debería conocer tanto el testimonio como el descubrimiento de la etiqueta. Tomás, en cambio, conservará su creencia inicial.

Repita el ejercicio entregando directamente el paraguas. Esta vez Elena conocerá el testimonio, pero no habrá descubierto la etiqueta.

Compare ambos recorridos. Los personajes siguen siendo los mismos, pero la información que posee Elena ha cambiado según sus decisiones.

* * *

Los hechos registran lo ocurrido; los conocimientos indican quién dispone de determinada información, mientras que las creencias representan interpretaciones que pueden ser correctas o equivocadas.

Esta separación permite que dos personajes participen en una misma historia sin compartir necesariamente una visión idéntica de sus acontecimientos.

**Compruebe su historia:** verifique que Tomás conserva su creencia sobre el paraguas en ambos recorridos y que Elena solamente conoce la etiqueta cuando la ha examinado.

En el siguiente ejercicio permitiremos que Elena comunique el descubrimiento a Tomás. Así aprenderemos a modificar creencias y relaciones mediante una conversación.

# 3.5. Conversaciones que producen consecuencias

Elena ha descubierto que las iniciales de la etiqueta no coinciden con las de la compañera mencionada por Tomás. Sin embargo, él todavía cree reconocer el paraguas, porque desconoce el hallazgo.

Ahora incorporaremos una conversación que permita modificar esa situación. Elena podrá mostrarle la etiqueta o guardar silencio. Su decisión determinará qué información recibe Tomás y cómo evoluciona la relación entre ambos.

El jugador no escogerá si Tomás cambia de opinión. Lo que puede decidir es si Elena comparte la información que ha descubierto.

Si Elena muestra la etiqueta, Tomás tendrá motivos para reconsiderar su interpretación. Si guarda silencio, él conservará su creencia inicial.

Esta diferencia es importante: **el jugador decide qué hace Elena, mientras que las reacciones de Tomás dependen de las reglas que el autor ha declarado para su personaje**.

* * *

En esta versión, Tomás reconsidera su testimonio cuando Elena le muestra la contradicción.

Podemos representar ese cambio mediante `set_belief`:

```json  
{  
  "op": "set_belief",  
  "character": "tomas",  
  "key": "paraguas_es_de_companera",  
  "value": false  
}  
```

El valor `false` indica que Tomás ya no sostiene la creencia anterior. No significa que haya descubierto quién es el verdadero propietario.

El cambio tampoco ocurre simplemente porque Elena haya examinado el paraguas. Debe producirse después de una interacción en que Tomás reciba la información.

* * *

La manera en que Elena conversa con Tomás también puede influir en la confianza que él siente hacia ella.

En nuestro ejemplo, Tomás aprecia que Elena le muestre el indicio y le permita revisar su recuerdo. Como consecuencia, su confianza hacia ella aumenta en un punto.

La relación tiene una dirección:

**Tomás → Elena: confianza +1**

Esto no implica que Elena confíe más en Tomás. Para modificar la relación inversa, el autor tendría que declarar otra consecuencia.

Las relaciones dirigidas permiten representar situaciones habituales: una persona puede confiar en otra sin que esa confianza sea recíproca, y dos personajes pueden interpretar de manera diferente la misma conversación.

* * *

Ejecute la cuarta versión del paquete:

```bash  
glauquir --developer --package paraguas_olvidado_etapa_4.package.json  
```

Examine el paraguas y seleccione la opción de mostrarle la etiqueta a Tomás. Después de la conversación, compruebe que recibió la información, que su creencia cambió y que aumentó su confianza hacia Elena.

Repita el ejercicio, pero esta vez guarde silencio.

Tomás deberá conservar su creencia inicial, porque Elena no le comunicó el descubrimiento. Tampoco debería recibir el aumento de confianza asociado a esa conversación.

En ambos recorridos podrá terminar la historia.

* * *

Una conversación puede tener consecuencias que van más allá del texto que aparece en pantalla. Puede transmitir información, modificar una creencia y cambiar una relación, siempre que el autor declare los efectos correspondientes.

En nuestro ejemplo, la reacción de Tomás es sencilla y determinista: cuando Elena le muestra la etiqueta, él reconsidera su interpretación. No estamos simulando todavía una deliberación compleja ni una personalidad autónoma; estamos enseñando a expresar una consecuencia narrativa coherente con la información recibida.

**Compruebe su historia:** compare los dos recorridos y verifique que solamente la conversación en que Elena comparte el indicio modifica la creencia y la confianza de Tomás.

En el siguiente ejercicio incorporaremos S.O.F.I.A., TRAITS y DICE para representar una situación con resultado incierto: Tomás intentará recordar otro detalle sobre el paraguas, pero no siempre lo conseguirá.

