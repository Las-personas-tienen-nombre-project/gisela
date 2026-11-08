# 1. Qué es GISELA y para qué sirve

GISELA es un motor para crear historias interactivas. Permite escribir relatos en los que las decisiones del lector y los acontecimientos pueden cambiar lo que sucede después.

En un relato tradicional, el autor establece qué ocurre y cómo lo cuenta. En GISELA, también define las condiciones para que algo suceda y las consecuencias de las acciones.

Por ejemplo, un personaje puede encontrar una llave, guardarla y utilizarla más adelante para abrir una puerta. Si no la tiene, deberá buscar otra solución. GISELA conserva lo sucedido y aplica las reglas que estableció el autor.

## Historias con reglas

Una historia puede contener escenas, conversaciones, elecciones, personajes, objetos, relaciones, objetivos y resultados variables. No es necesario utilizar todo eso en un mismo relato. Una historia con una decisión y dos finales también es una historia completa.

El autor define las posibilidades. GISELA comprueba las condiciones, ejecuta las acciones permitidas y conserva sus consecuencias.

## Componentes principales

| Componente | Función |
| --- | --- |
| GISELA | Ejecuta la historia y controla sus reglas. |
| ALBERTO | Representa el mundo, los personajes, los objetos y sus relaciones. |
| S.O.F.I.A. | Ofrece cinco atributos opcionales para personajes. |
| TRAITS | Calcula la contribución de rasgos declarados. |
| DICE | Realiza evaluaciones numéricas con azar reproducible. |
| MARY | Evalúa el progreso de objetivos y misiones. |
| GLAUQUIR | Permite leer y jugar historias desde una interfaz de texto. |

No necesitas aprender todos estos componentes para comenzar. Los conocerás cuando los utilices en los talleres. Las [definiciones del proyecto](../../../README.md#core-definitions) explican sus responsabilidades con mayor detalle.

## Cómo se escribe una historia

Las historias se guardan en paquetes narrativos que contienen textos y reglas. Actualmente se escriben con el lenguaje DSL 1.5, representado mediante archivos JSON.

No necesitas programar en Python, pero aprenderás algunas reglas de JSON. Comenzaremos con un relato preparado, que podrás modificar y comprobar.

## Qué aprenderás

Primero crearás una historia sencilla con decisiones y finales. Después podrás incorporar personajes, conversaciones, objetos y otras reglas, según las capacidades comprobadas del motor.

Continúa con [Casos de uso](02_casos_de_uso.md).
