# Algoritmo Genético Ordinal — TSP

**Asignación 1 · Inteligencia Artificial · UAG**

Implementación de un **algoritmo genético con codificación ordinal** para resolver el clásico *Traveling Salesman Problem* (Problema del Agente Viajero) en Python.

---

## ¿Qué es la codificación ordinal?

En la codificación ordinal cada gen del cromosoma representa el **índice** de una ciudad dentro de una *lista de referencia* que se va reduciendo. Esto permite aplicar operadores genéticos estándar (cruce de un punto, mutación por reinicio) **sin generar rutas inválidas**.

### Ejemplo de codificación (4 ciudades, ruta `[2, 0, 3, 1]`)

| Paso | Lista de referencia | Ciudad elegida | Gen |
|------|---------------------|----------------|-----|
| 1 | `[0, 1, 2, 3]` | ciudad 2 → pos **2** | 2 |
| 2 | `[0, 1, 3]`    | ciudad 0 → pos **0** | 0 |
| 3 | `[1, 3]`       | ciudad 3 → pos **1** | 1 |
| 4 | `[1]`          | ciudad 1 → pos **0** | 0 |

**Cromosoma** = `[2, 0, 1, 0]`  →  decodifica a la ruta `[2, 0, 3, 1]`

---

## Operadores del algoritmo

| Componente | Estrategia |
|------------|------------|
| Representación | Ordinal |
| Inicialización | Aleatoria (cromosomas válidos) |
| Selección | Torneo (*k* = 5) |
| Cruce | Un punto (*one-point crossover*) |
| Mutación | Reinicio aleatorio de gen |
| Reemplazo | Elitismo + nueva generación |

---

## Parámetros por defecto

| Parámetro | Valor |
|-----------|-------|
| Tamaño de población | 200 |
| Generaciones | 1 000 |
| Tasa de mutación | 0.02 (2 %) |
| Tasa de cruce | 0.85 (85 %) |
| Tamaño de torneo | 5 |
| Élite | 2 individuos |

---

## Ejecución

Solo requiere Python 3.10+ (sin dependencias externas):

```bash
python3 genetic_tsp.py
```

## Resultado de ejemplo

```
  Gen    0 │ Mejor =   12489.56  │ Promedio =   15743.93  │ Tiempo =   0.0s
  Gen  100 │ Mejor =    7150.56  │ Promedio =    8346.67  │ Tiempo =   0.8s
  ...
  Gen  999 │ Mejor =    6456.40  │ Promedio =    7583.88  │ Tiempo =   7.2s

  Mejor distancia encontrada : 6456.40
  Mejora total               : 48.3%
```

---

## Estructura del proyecto

```
.
├── genetic_tsp.py   # Implementación completa del algoritmo
└── README.md        # Este archivo
```
