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


# Continuación del tutorial

# 3.1. Del relato al guion productivo

[Leer este capítulo](GISLEA_primera_aventura_paquete.md#31-del-relato-al-guion-productivo).

# 3.2. Crear y ejecutar el primer paquete

[Leer este capítulo](GISLEA_primera_aventura_paquete.md#32-crear-y-ejecutar-el-primer-paquete).

# 3.3. Dar estado a la historia

[Leer este capítulo](GISLEA_primera_aventura_paquete.md#33-dar-estado-a-la-historia).

# 3.4. Lo que saben y creen los personajes

[Leer este capítulo](GISLEA_primera_aventura_paquete.md#34-lo-que-saben-y-creen-los-personajes).

# 3.5. Conversaciones que producen consecuencias

[Leer este capítulo](GISLEA_primera_aventura_paquete.md#35-conversaciones-que-producen-consecuencias).

# 3.6. La ficha de personaje: atributos, rasgos y azar

[Leer este capítulo](GISLEA_primera_aventura_sistemas.md#36-la-ficha-de-personaje-atributos-rasgos-y-azar).

# 3.7. Objetivos y misiones con MARY

[Leer este capítulo](GISLEA_primera_aventura_sistemas.md#37-objetivos-y-misiones-con-mary).

# 3.8. Comprobar y depurar nuestra historia

[Leer este capítulo](GISLEA_primera_aventura_sistemas.md#38-comprobar-y-depurar-nuestra-historia).

