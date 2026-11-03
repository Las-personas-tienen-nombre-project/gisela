Manual de Gisela
================

**By El Programador Pobre**



GISELA — Mi primera historia interactiva
========================================

*Guía práctica para construir historias interactivas sin conocimientos previos de programación.*

# 1. Introducción a GISELA

GISELA es un motor narrativo que permite construir historias interactivas mediante personajes, escenas, acontecimientos, decisiones y consecuencias. En lugar de programar individualmente cada situación, el autor describe qué puede suceder, bajo qué circunstancias y qué cambios deben producirse cuando ocurre algo.

Para hacerlo, GISELA dispone de un lenguaje declarativo de dominio específico, también llamado DSL. Aunque su nombre resulte técnico, la idea es sencilla: el escritor prepara archivos que describen los elementos y las reglas de su historia, mientras que GISELA se encarga de interpretarlos y ejecutarlos.

El motor conserva información sobre lo sucedido durante la partida. Esto permite, por ejemplo, que un personaje recuerde una conversación anterior, que una decisión deje de estar disponible porque ya ocurrió determinado acontecimiento o que dos personajes mantengan opiniones diferentes sobre un mismo hecho.

GISELA no escribe diálogos ni inventa acontecimientos por cuenta propia. El autor sigue siendo responsable de la historia y de sus posibilidades; el motor proporciona los mecanismos necesarios para ejecutarlas de manera coherente.

* * *

En una historia interactiva sencilla, el lector puede escoger entre dos alternativas y continuar por una de ellas. A medida que aumentan las decisiones y sus consecuencias, el autor debe considerar también qué ocurrió anteriormente, qué información posee cada personaje y qué situaciones siguen siendo posibles.

Una manera de resolverlo consiste en escribir rutas diferentes para cada combinación. Este procedimiento es válido, pero puede resultar difícil de mantener cuando muchas decisiones influyen en acontecimientos posteriores.

GISELA permite organizar parte de esa complejidad mediante un estado narrativo. En vez de escribir una versión completa de una escena para cada circunstancia, el autor puede declarar las condiciones que determinan qué acciones y acontecimientos corresponden al estado actual de la historia.

Imaginemos que una joven conoce a un muchacho durante su jornada de trabajo. Puede encontrarlo simpático, escuchar una conversación que aumente su curiosidad y descubrir que confía en él más de lo que esperaba. Sin embargo, ninguna de esas circunstancias obliga a que decida acercarse. Su interés y su decisión de actuar pueden representarse por separado.

Esta distinción es especialmente útil cuando el autor quiere construir personajes que conserven conocimientos, creencias y relaciones propias, en lugar de reaccionar únicamente a la última opción escogida por el jugador.

* * *

GISELA puede utilizarse en distintos tipos de narrativa interactiva.

**Ficción interactiva textual.** Historias que presentan lugares, diálogos y decisiones mediante texto, sin exigir ilustraciones ni recursos audiovisuales.

**Novelas visuales.** Relatos que combinan diálogos, personajes, imágenes y música. GISELA administra la lógica narrativa, mientras que un cliente como Ren'Py puede encargarse de la presentación audiovisual.

**Misterios e investigaciones.** Historias en que los personajes poseen información incompleta, interpretan indicios, sostienen creencias equivocadas o descubren acontecimientos anteriores.

**Relaciones entre personajes.** Relatos en que la confianza, la afinidad, las experiencias compartidas y las circunstancias modifican las posibilidades de interacción.

**Historias con incertidumbre.** Situaciones en que determinadas acciones pueden tener resultados diferentes, utilizando mecanismos probabilísticos reproducibles.

Estos ejemplos no son categorías excluyentes. Una misma historia puede combinar investigación, relaciones personales y acontecimientos sujetos al azar.

* * *

El autor prepara un **paquete narrativo** que contiene los elementos y las declaraciones de su historia. GISELA comprueba que el paquete cumpla sus contratos, interpreta sus reglas y administra el estado de cada partida.

Para jugar o probar la historia se utiliza un **cliente**, es decir, un programa que presenta lo que ocurre y permite seleccionar acciones.

En este manual trabajaremos con GLAUQUIR, un cliente de terminal que permite recorrer las historias mediante texto e inspeccionar su funcionamiento. No será necesario preparar ilustraciones ni construir una interfaz gráfica.

Una vez terminado, el mismo paquete narrativo puede servir como base para otros clientes compatibles. La presentación cambia, pero la lógica narrativa permanece en GISELA.

* * *

Aprenderemos mediante un ejercicio llamado *El paraguas olvidado*.

Elena encuentra un paraguas azul en una estación de tren. Tomás, otro pasajero, cree reconocerlo y asegura haber visto a una compañera de trabajo dejarlo allí. Sin embargo, Elena puede descubrir un indicio que contradice su testimonio.

A partir de esta situación construiremos personajes, objetos, escenas, decisiones y consecuencias. Después incorporaremos conocimientos, creencias, relaciones y una evaluación probabilística, hasta obtener una historia completa que pueda ejecutarse con GLAUQUIR.

El propósito no es escribir una obra extensa ni utilizar todas las capacidades de GISELA, sino aprender a transformar un relato en un guion productivo: **un conjunto de declaraciones que el motor puede interpretar y ejecutar**.

No necesita saber programar para comenzar. En las páginas siguientes conocerá las herramientas indispensables, aprenderá lo necesario para trabajar con archivos JSON y construirá su primera historia paso a paso.

2. Componentes y herramientas de GISELA
=======================================

Para construir una historia interactiva con GISELA necesitamos tres cosas: un guion que describa la historia y sus reglas, un motor que pueda interpretarlas y una herramienta que nos permita recorrerla. GISELA proporciona el motor y el cliente GLAUQUIR; el autor se encarga de preparar el guion utilizando su lenguaje declarativo.

En esta sección conoceremos las piezas fundamentales del sistema y prepararemos las herramientas que utilizaremos durante el workshop.

# 2.1. El guion productivo

Llamaremos **guion productivo** al conjunto de declaraciones que permite ejecutar una historia. A diferencia de un manuscrito narrativo, que contiene los acontecimientos tal como los leería una persona, el guion productivo también debe establecer qué acciones son posibles, cuándo pueden realizarse y cuáles serán sus consecuencias.

En GISELA, esas declaraciones forman un *paquete narrativo*. El paquete contiene las definiciones necesarias para ejecutar la historia, como personajes, escenas, acontecimientos, acciones, condiciones y finales.

El autor utiliza un lenguaje declarativo de dominio específico, o DSL, cuya representación actual está basada en JSON. No necesita escribir funciones de Python para definir el comportamiento de cada escena.

Los **schemas** y contratos de GISELA establecen qué declaraciones son válidas. Antes de ejecutar una historia, el motor comprueba tanto su estructura como las relaciones entre sus componentes. Este proceso se denomina *admisión*.

Un archivo puede estar correctamente escrito en JSON y, aun así, no constituir un paquete válido de GISELA. Por ejemplo, podría mencionar una escena que no existe o utilizar una operación que el motor no admite.

# 2.2. Los componentes narrativos

GISELA dispone de varios componentes que cumplen funciones diferentes. No es obligatorio utilizarlos todos: su elección depende de lo que la historia necesite.

| Componente | Función | Ejemplo |  
|---|---|---|  
| **ALBERTO** | Estado del mundo, conocimientos, creencias y relaciones | Tomás cree que reconoce el paraguas, pero Elena conoce un indicio que él desconoce |  
| **S.O.F.I.A.** | Atributos numéricos de personajes | La atención de Tomás interviene cuando intenta recordar un detalle |  
| **TRAITS** | Rasgos que pueden contribuir a evaluaciones según el contexto | Un rasgo relacionado con la observación modifica una evaluación |  
| **DICE** | Evaluación matemática de resultados inciertos | Determinar si Tomás consigue recordar |  
| **MARY** | Seguimiento de objetivos y misiones | Registrar cuándo Elena resuelve qué hacer con el paraguas |

Estos componentes se complementan, pero no deben confundirse.

Por ejemplo, que Tomás tenga buena capacidad de observación es una característica de su personaje; que conozca un detalle sobre el paraguas es información adquirida; y que consiga recordarlo durante una conversación puede depender de una evaluación probabilística. Son tres asuntos diferentes, que conviene representar por separado.

Durante el workshop utilizaremos cada componente solamente cuando aparezca una necesidad narrativa que justifique su intervención.

# 2.3. GLAUQUIR: recorrer y comprobar la historia

GLAUQUIR es el cliente de terminal incluido con GISELA. Permite ejecutar un paquete narrativo, leer lo que ocurre y seleccionar las acciones disponibles.

Una terminal es una ventana en la que se escriben instrucciones de texto. Aunque inicialmente pueda parecer menos familiar que una aplicación con botones, para nuestro propósito ofrece una ventaja: permite comprobar el comportamiento de una historia sin preparar ilustraciones, animaciones ni pantallas especiales.

En GLAUQUIR podremos leer descripciones, conversar con personajes, examinar elementos y tomar decisiones. También dispone de herramientas de desarrollo para consultar hechos, relaciones y otros aspectos del estado narrativo.

Esto será importante cuando necesitemos distinguir entre lo que escribimos en el guion y lo que el motor registró realmente.

GLAUQUIR no es GISELA en su totalidad. Es uno de los clientes que pueden utilizar su motor, del mismo modo que una integración con Ren'Py puede presentar una historia mediante una interfaz de novela visual.

# 2.4. Preparar las herramientas

Para realizar los ejercicios necesitaremos una instalación compatible de Python, GISELA, un editor de texto y una terminal.

Python es el lenguaje en que está implementado el motor. No tendremos que aprender a programar en Python, pero necesitamos que esté instalado para utilizar la distribución de GISELA empleada en este manual.

La versión examinada requiere Python 3.10 o posterior.

Una vez obtenida la distribución del proyecto, abriremos una terminal en su carpeta principal. En Windows, Linux y macOS, los pasos para abrirla pueden variar, pero los comandos de GISELA serán los mismos una vez que esté instalado y activado el entorno correspondiente.

La instalación desde los archivos del proyecto utiliza:

```bash  
python -m pip install -e .  
```

Este comando instala GISELA desde la carpeta actual. En algunos sistemas, Python se ejecuta mediante `python3` o `py`, por lo que debe utilizarse el nombre disponible en el equipo.

Para evitar conflictos con otras aplicaciones de Python, se recomienda trabajar dentro de un entorno virtual. Las instrucciones específicas de creación y activación para cada sistema se incluyen en la guía de instalación que acompaña a la distribución didáctica.

Después de instalar, podemos comprobar el funcionamiento mediante una historia incluida con GISELA:

```bash  
glauquir  
```

GLAUQUIR abrirá su historia predeterminada. Para salir, podemos utilizar el comando de salida documentado por el cliente o cerrar la sesión desde la terminal.

# 2.5. JSON en pocas palabras

JSON es una forma de escribir información estructurada mediante texto. No es un lenguaje de programación: permite declarar datos que otros programas pueden leer.

Observe este ejemplo:

```json  
{  
  "nombre": "Tomás",  
  "atencion": 5,  
  "lleva_paraguas": false,  
  "objetos": ["bolso", "billete"]  
}  
```

Las llaves `{ }` delimitan un objeto y los corchetes `[ ]` contienen una lista. Cada dato tiene un nombre, llamado *clave*, y un valor. Los textos se escriben entre comillas dobles, los números sin comillas y los valores lógicos se representan mediante `true` o `false`.

Los datos se separan mediante comas, excepto el último elemento de cada objeto o lista.

Este ejemplo sirve únicamente para comprender la escritura de JSON; **no es una declaración válida de personaje GISELA**. En el workshop utilizaremos las claves y estructuras que establecen los contratos reales del motor.

No necesita memorizar todas las reglas de JSON antes de comenzar. Aprenderemos las estructuras que vayamos utilizando y emplearemos la validación de GISELA para detectar posibles errores.

# 2.6. Validar y ejecutar un paquete

GISELA proporciona una herramienta para comprobar los paquetes narrativos antes de utilizarlos.

Si nuestro archivo se llama `mi_historia.package.json`, podemos validarlo mediante:

```bash  
gisela validate mi_historia.package.json  
```

La herramienta informa si el paquete puede admitirse o si contiene problemas que debemos corregir.

Una vez validado, podemos ejecutarlo en GLAUQUIR:

```bash  
glauquir --package mi_historia.package.json  
```

El nombre del archivo debe coincidir con el que realmente hayamos creado. Si se encuentra en otra carpeta, tendremos que indicar su ruta.

Durante la ejecución, GLAUQUIR mostrará las acciones disponibles. El autor podrá recorrer la historia y verificar si los acontecimientos ocurren bajo las condiciones esperadas.

La validación comprueba que el paquete cumple los contratos correspondientes, pero no garantiza que la historia tenga sentido o que todos sus caminos lleguen a un desenlace. Eso requiere probar las decisiones, revisar el estado y comprobar los resultados.

# 2.7. Qué necesitamos comprender antes de continuar

Hasta aquí basta con distinguir cuatro responsabilidades:

**El autor** escribe la historia y declara sus posibilidades.

**El DSL y sus contratos** establecen cómo expresar esas declaraciones y cuáles son válidas.

**El motor GISELA** ejecuta las reglas y conserva el estado narrativo.

**GLAUQUIR** presenta la historia y permite recorrerla y examinar sus resultados.

En la siguiente sección comenzaremos el workshop de *El paraguas olvidado*. Primero identificaremos sus personajes, acontecimientos y decisiones en lenguaje natural; después convertiremos esa información en declaraciones del DSL y construiremos un paquete que pueda ejecutarse en GLAUQUIR.

# 2.4. Instalación de GISELA

Para realizar el workshop necesita Python, los archivos de GISELA y un editor de texto. No es necesario instalar Ren'Py.

GISELA requiere Python 3.10 o posterior.

**Windows:** descargue Python desde https://www.python.org/downloads/ e instálelo. Compruebe que los comandos de Python estén disponibles en la terminal.

**Linux:** utilice el administrador de paquetes de su distribución para instalar Python 3 y el módulo que permite crear entornos virtuales. En Ubuntu y Debian puede utilizar:

```bash  
sudo apt install python3 python3-venv python3-pip  
```

**macOS:** puede instalar Python desde https://www.python.org/downloads/ utilizando el instalador correspondiente.

Para comprobar la instalación, abra una terminal y ejecute:

```bash  
python --version  
```

En algunos sistemas deberá utilizar `python3` y, en Windows, puede que corresponda `py`.

* * *

Descomprima la distribución de GISELA en una carpeta de trabajo, por ejemplo `Documentos/GISELA`.

Abra una terminal dentro de esa carpeta. Debe encontrarse en el directorio que contiene el archivo `pyproject.toml`.

Trabajaremos con los archivos de la distribución fuente de GISELA. Si dispone de una instalación preparada especialmente para el workshop, utilice las instrucciones que la acompañan.

* * *

Un entorno virtual permite instalar GISELA sin mezclar sus dependencias con las de otros programas.

En **Windows**, utilizando PowerShell:

```powershell  
py -m venv .venv  
.\.venv\Scripts\python.exe -m pip install -e .  
```

En **Linux y macOS**:

```bash  
python3 -m venv .venv  
./.venv/bin/python -m pip install -e .  
```

El comando `pip install -e .` instala GISELA desde la carpeta actual. No necesita instalar las dependencias de pruebas del desarrollador para completar el workshop.

* * *

En Windows:

```powershell  
.\.venv\Scripts\gisela.exe --help  
.\.venv\Scripts\glauquir.exe --help  
```

En Linux y macOS:

```bash  
./.venv/bin/gisela --help  
./.venv/bin/glauquir --help  
```

Si aparecen las opciones de los programas, la instalación está preparada.

Para iniciar una historia de ejemplo, desde la raíz de la distribución:

**Windows:**

```powershell  
.\.venv\Scripts\glauquir.exe --package gisela/packages/h46_faro_de_niebla.package.json  
```

**Linux y macOS:**

```bash  
./.venv/bin/glauquir --package gisela/packages/h46_faro_de_niebla.package.json  
```

GLAUQUIR mostrará el escenario y las acciones disponibles. Ya puede comenzar a trabajar.

# 2.5. JSON en pocas palabras

JSON permite escribir datos estructurados mediante texto. Las llaves contienen objetos, los corchetes contienen listas y cada dato tiene una clave y un valor.

```json  
{  
  "nombre": "Tomás",  
  "atencion": 5,  
  "lleva_paraguas": false,  
  "objetos": ["bolso", "billete"]  
}  
```

Los textos se escriben entre comillas dobles; los números y los valores `true` y `false`, sin comillas. Los elementos se separan mediante comas, excepto el último.

Este ejemplo enseña cómo se escribe JSON, pero no constituye una declaración válida de personaje GISELA. En el workshop utilizaremos las claves reales del DSL.

Puede editar los archivos con cualquier editor que permita guardar texto plano. Conviene utilizar uno que destaque la sintaxis JSON para identificar con facilidad comillas, comas y llaves.

# 2.6. Validar y ejecutar una historia

Cada vez que prepare un paquete narrativo, compruebe primero que GISELA pueda admitirlo.

En Windows:

```powershell  
.\.venv\Scripts\gisela.exe validate mi_historia.package.json  
```

En Linux y macOS:

```bash  
./.venv/bin/gisela validate mi_historia.package.json  
```

Si la validación es satisfactoria, ejecútelo en GLAUQUIR:

**Windows:**

```powershell  
.\.venv\Scripts\glauquir.exe --package mi_historia.package.json  
```

**Linux y macOS:**

```bash  
./.venv/bin/glauquir --package mi_historia.package.json  
```

Sustituya `mi_historia.package.json` por el nombre real de su archivo.

**Si aparece un error**, compruebe primero que está utilizando la carpeta correcta, que el archivo existe y que los comandos se ejecutan mediante el entorno virtual creado. Si falla la admisión, lea el diagnóstico antes de modificar el contenido: un JSON sintácticamente correcto puede incumplir los contratos de GISELA.

La validación confirma que el paquete cumple los contratos, pero no garantiza que todos sus caminos narrativos funcionen. Eso lo comprobaremos jugando e inspeccionando los resultados en GLAUQUIR.

3. Workshop: construir una historia con GISELA
==============================================

En este taller construiremos *El paraguas olvidado*, una historia breve que irá adquiriendo capacidades a medida que las necesitemos. Comenzaremos con personajes, una situación y dos desenlaces; luego incorporaremos acciones, hechos, conocimientos, relaciones, atributos, rasgos, azar y objetivos.

Al terminar dispondremos de un paquete ejecutable en GLAUQUIR.

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


