# Referencia de Clase — Algoritmos Genéticos / TSP
**Universidad Autónoma de Guadalajara · A World by Arizona State University**
**Asignación 1 · Inteligencia Artificial**

---

## Transcripción completa

> **0:11** — Algoritmos genéticos: la computación evolutiva. Evolucionar y computation es un campo de la inteligencia artificial abocada a la optimización y la búsqueda de soluciones mediante el uso de algoritmos que tratan de imitar el fenómeno natural de la evolución. Los más relevantes son los algoritmos genéticos, la programación genética y los algoritmos meméticos.

> **0:47** — **Algoritmos genéticos**: algoritmo evolutivo que abstrae el proceso de cruzada y selección natural y lo aplican a modelos computacionales de información genética. Es el más utilizado.

> **1:05** — **Programación genética**: realiza un proceso evolutivo sobre ramas de operadores lógicos con el propósito de obtener secuencias lógicas matemáticas que pueden optimizar o sintetizar funciones, e incluso llegar a generar líneas de código para programas de uso específico.

> **1:22** — **Algoritmos meméticos**: similares en la estructura general a los algoritmos genéticos pero con especificaciones culturales tanto en el proceso de reproducción y evaluación de la función de aptitud, ya que se puede intercambiar información entre individuos y establecer entornos de evolución guiada mediante el uso de metaheurísticas y optimización local determinísticos.

> **1:59** — La antena 2006 de la nave espacial de la NASA ST5 fue encontrada por un programa evolutivo de diseño de computadora para crear el mejor patrón de radiación. Se conoce como una antena evolucionada.

> **2:25** — Los algoritmos genéticos fueron desarrollados por **John Holland** alrededor de **1970**.

> **2:32** — Los algoritmos genéticos se inspiran en el fenómeno evolutivo y algunos elementos de la genética.

> **2:45** — **Nomenclatura (paralelismo con genética)**:
> - **Gen**: dato numérico o carácter
> - **Alelo**: subcomponentes binarios del gen
> - **Cromosoma**: conjunto de números agrupados en un vector unidimensional
> - **Población**: conjunto de vectores/cromosomas dentro del algoritmo genético

> **3:34** — Michalewicz, en su libro *Genetic Algorithms + Data Structures = Evolution Programs*, propone el siguiente ejercicio mental para explicar el proceso evolutivo:

> **3:52** — Existe una población de conejos clasificados en cuatro grupos: rápidos, listos, lentos y tontos. Los rápidos y listos tienen mayores probabilidades de sobrevivir. Los supervivientes serán en promedio más aptos. Al reproducirse, la siguiente generación será más apta que la precedente. La aptitud promedio de la población irá en aumento conforme pasen las generaciones.

> **5:16** — Detrás de esta mejora está el proceso de **selección natural**, donde los más aptos tienen mayores posibilidades de sobrevivir y de reproducirse.

> **5:34** — Holland propuso el **Teorema de Esquemas**, explicado por David Goldberg en *Genetic Algorithms in Search, Optimization and Machine Learning*: subsecciones arbitrarias de individuos (cromosomas) que son más aptas tendrán mayores posibilidades de encontrar réplicas de sí mismas en generaciones subsecuentes. Estos segmentos viajan como *bloques constructivos* a través de individuos, contribuyendo a formar soluciones subóptimas.

> **6:39** — El **Problema del Agente Viajero (TSP)** es una gran forma de introducirse al diseño de un algoritmo genético. Se trata de un agente que debe visitar un conjunto total de ciudades recorriendo la ruta más corta posible. Es un problema **NP-completo**.

> **7:09** — Los problemas NP-completos requieren espacio y tiempo en escalas mayúsculas para ser resueltos de manera exhaustiva. Para estas situaciones, métodos no convencionales como los algoritmos genéticos son de gran utilidad.

> **7:40** — Para este caso particular desarrollaremos un **algoritmo genético del tipo ordinal**.

> **8:45** — Con 3 ciudades existen 3! = **6 rutas** posibles. Con 20 ciudades: **20! rutas** posibles. Si una computadora evaluara 1,000,000 rutas/segundo, tardaría ~**80,000 años** en evaluarlas todas exhaustivamente.

> **11:22** — **Paso 1**: Crear aleatoriamente una población de **100 cromosomas de longitud 20** (arreglo de 100×20). Solo para la primera generación.

> **12:00** — Cada gen representa la etiqueta numérica (1 al 20) de una ciudad. Cada cromosoma representa una propuesta de ruta.

> **12:51** — **Paso 2**: Calcular la distancia total de cada recorrido aplicando la fórmula de **distancia entre dos puntos** entre pares de ciudades consecutivas en el cromosoma.

> **14:39** — **El Torneo** representa el proceso de selección: pseudo-aleatoriamente se elige un subconjunto de cromosomas, se verifica su función de aptitud y se elige al mejor (ruta más corta).

> **16:36** — Para este ejercicio: torneo del **5% de la población** (5 de 100). Se realizan **100 torneos por generación** para obtener 100 padres (un cromosoma puede ganar más de un torneo).

> **17:49** — **Dos mecanismos de reproducción** (elegidos pseudo-aleatoriamente):
>
> **Enroque**: seleccionar dos bloques de igual longitud dentro del cromosoma (inicio y dimensión variables) e intercambiarlos entre sí. El resultado es el hijo.
>
> **Inversión**: elegir un solo bloque (inicio y longitud variables) e invertirlo. El cromosoma alterado es el hijo.

> **19:15** — La **inversión** es particularmente útil en TSP porque puede deshacer bucles en el recorrido, acercándose a la solución óptima.

> **20:02** — Una vez con los 100 hijos, se evalúa cada uno y se registra su función de aptitud. La **matriz de hijos reemplaza a la de padres** y se vuelve al torneo.

> **20:30** — Se usa un **ciclo for de 100 iteraciones** (generaciones).

---

## Pasos del algoritmo (resumen del profesor)

| Paso | Descripción |
|------|-------------|
| 1 | Crear población inicial: 100 cromosomas × 20 genes (solo 1ª generación) |
| 2 | Calcular distancia de recorrido por cromosoma (distancia entre puntos) |
| 3 | Registrar distancia en columna adicional de cada cromosoma |
| 4 | Abrir ciclo `for` principal: 100 generaciones |
| 5 | Usar matriz actual (padres o hijos convertidos en padres) |
| 6 | Realizar **100 torneos** (5% de población = 5 candidatos cada uno) |
| 7 | Elegir ganador: cromosoma con ruta más corta |
| 8 | A cada ganador (padre) aplicar aleatoriamente: **enroque** o **inversión** |
| 9 | Obtener 1 hijo por torneo → 100 hijos por generación |
| 10 | Conformar nueva matriz de hijos y reemplazar la de padres |
| 11 | Imprimir ruta del mejor individuo y graficar menor distancia por generación |
| 12 | Cerrar ciclo `for` principal |

---

## Requisitos de entrega

- **Formato**: Video del código en ejecución (máx. **2 minutos**)
- **Plataforma**: YouTube como **oculto (unlisted)**
- **Subir a plataforma**: solo la liga del video

### Ventanas requeridas en el video

**Ventana 1 — Ruta del agente viajero:**
- Graficar la ruta del individuo más apto por generación
- Actualizar cada vez que se completa una nueva generación
- Mostrar la distancia más corta obtenida por generación

**Ventana 2 — Función de aptitud:**
- Eje Y: distancia total del recorrido del individuo más apto
- Eje X: número de generación
- Graficar en tiempo real conforme avanza el algoritmo

---

## Diferencias entre la implementación actual y la especificación del profesor

| Aspecto | Implementación actual | Especificación del profesor |
|---------|----------------------|----------------------------|
| Ciudades | 25 | 20 |
| Población | 200 | 100 |
| Generaciones | 1,000 | 100 |
| Torneo | k=5 | 5% de 100 = 5 |
| Operador 1 | Cruce de un punto | Enroque (swap de dos bloques iguales) |
| Operador 2 | Mutación por reinicio | Inversión (invertir un bloque) |
| Visualización | Solo consola | 2 ventanas gráficas en tiempo real |
