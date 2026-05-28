"""
================================================================
  ALGORITMO GENÉTICO ORDINAL — PROBLEMA DEL AGENTE VIAJERO
  (TSP – Traveling Salesman Problem)
================================================================
  Asignación 1 · Inteligencia Artificial · UAG

  Especificaciones:
  ┌─────────────────────────────────────────────────────────┐
  │  Ciudades            : 20                               │
  │  Población           : 100 cromosomas                   │
  │  Generaciones        : 100                              │
  │  Torneo              : 5% (5 candidatos de 100)         │
  │  Reproducción        : Enroque  o  Inversión (50/50)    │
  │  Codificación        : Ordinal                          │
  │  Visualización       : 2 ventanas gráficas en tiempo    │
  │                        real (ruta + función de aptitud) │
  └─────────────────────────────────────────────────────────┘
================================================================
"""

import math
import random
import sys
import matplotlib
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────
#  CIUDADES — 20 puntos en plano cartesiano
#  Etiqueta visual: C1..C20  |  Índice interno: 0..19
# ──────────────────────────────────────────────────────────────
CITIES = [
    ( 1,  3), ( 3,  1), ( 5,  2), ( 7,  1), ( 9,  3),
    (10,  5), ( 9,  7), ( 7,  9), ( 5, 10), ( 3,  9),
    ( 1,  7), ( 2,  5), ( 4,  4), ( 6,  3), ( 8,  5),
    ( 7,  7), ( 5,  6), ( 3,  6), ( 4,  8), ( 6,  8),
]
N = len(CITIES)   # 20

# ──────────────────────────────────────────────────────────────
#  PARÁMETROS DEL ALGORITMO
# ──────────────────────────────────────────────────────────────
POP_SIZE        = 100   # individuos por generación
GENERATIONS     = 100   # iteraciones del ciclo principal
TOURNAMENT_SIZE = 5     # 5 % de la población = 5 de 100
SEED            = 42    # reproducibilidad

random.seed(SEED)


# ══════════════════════════════════════════════════════════════
#  CODIFICACIÓN ORDINAL
# ══════════════════════════════════════════════════════════════

def encode(route: list) -> list:
    """
    Permutación → cromosoma ordinal.

    Para cada ciudad de la ruta se busca su posición en la lista
    de referencia restante y ese índice se guarda como gen.
    Gen i tiene rango válido [0, N-1-i].

    Ejemplo  ruta=[2,0,3,1], N=4:
      ref=[0,1,2,3] → ciudad 2 en pos 2 → gen=2, ref=[0,1,3]
      ref=[0,1,3]   → ciudad 0 en pos 0 → gen=0, ref=[1,3]
      ref=[1,3]     → ciudad 3 en pos 1 → gen=1, ref=[1]
      ref=[1]       → ciudad 1 en pos 0 → gen=0
      Cromosoma = [2, 0, 1, 0]
    """
    ref = list(range(N))
    chrom = []
    for city in route:
        idx = ref.index(city)
        chrom.append(idx)
        ref.pop(idx)
    return chrom


def decode(chrom: list) -> list:
    """
    Cromosoma ordinal → permutación (proceso inverso).

    Cada gen indica el índice en la lista de referencia restante
    desde donde se extrae la próxima ciudad.
    """
    ref = list(range(N))
    route = []
    for gene in chrom:
        idx = min(gene, len(ref) - 1)   # clamping de seguridad
        route.append(ref[idx])
        ref.pop(idx)
    return route


# ══════════════════════════════════════════════════════════════
#  FUNCIÓN DE FITNESS (aptitud)
# ══════════════════════════════════════════════════════════════

def euclidean(a: int, b: int) -> float:
    """Distancia euclidiana entre las ciudades a y b."""
    dx = CITIES[a][0] - CITIES[b][0]
    dy = CITIES[a][1] - CITIES[b][1]
    return math.sqrt(dx * dx + dy * dy)


def route_distance(route: list) -> float:
    """Distancia total del recorrido circular (suma de tramos consecutivos)."""
    return sum(
        euclidean(route[i], route[(i + 1) % N])
        for i in range(N)
    )


def fitness(chrom: list) -> float:
    """Aptitud = distancia total de la ruta decodificada (menor = mejor)."""
    return route_distance(decode(chrom))


# ══════════════════════════════════════════════════════════════
#  INICIALIZACIÓN DE LA POBLACIÓN
# ══════════════════════════════════════════════════════════════

def random_chromosome() -> list:
    """
    Genera un cromosoma ordinal aleatorio válido.
    Gen i ∈ [0, N-1-i] garantiza siempre una ruta decodificable.
    """
    return [random.randint(0, N - 1 - i) for i in range(N)]


def initialize_population() -> list:
    """Paso 1: Crear aleatoriamente 100 cromosomas de longitud 20."""
    return [random_chromosome() for _ in range(POP_SIZE)]


# ══════════════════════════════════════════════════════════════
#  SELECCIÓN — Torneo
# ══════════════════════════════════════════════════════════════

def tournament_select(population: list, fitnesses: list) -> list:
    """
    Selección por torneo (Paso 6-7).

    Se eligen pseudo-aleatoriamente 5 candidatos de la población
    (5 % de 100). El cromosoma con menor distancia es el ganador
    y podrá reproducirse.  Un mismo cromosoma puede ganar más de
    un torneo; el tamaño acotado del torneo modera este privilegio.
    """
    indices = random.sample(range(POP_SIZE), TOURNAMENT_SIZE)
    winner  = min(indices, key=lambda i: fitnesses[i])
    return population[winner][:]


# ══════════════════════════════════════════════════════════════
#  OPERADORES DE REPRODUCCIÓN (Paso 8)
# ══════════════════════════════════════════════════════════════

def enroque(route: list) -> list:
    """
    Operador ENROQUE: selecciona dos bloques de igual longitud
    dentro del cromosoma (inicio y dimensión variables pero siempre
    de igual largo entre sí) e intercambia ambos segmentos.

    Este intercambio genera rutas diferentes que mantienen la
    validez de la permutación.
    """
    length  = random.randint(1, max(1, N // 4))
    max_p1  = N - 2 * length
    if max_p1 < 0:
        return route[:]
    pos1 = random.randint(0, max_p1)
    pos2 = random.randint(pos1 + length, N - length)

    child = route[:]
    child[pos1:pos1 + length], child[pos2:pos2 + length] = \
        child[pos2:pos2 + length], child[pos1:pos1 + length]
    return child


def inversion(route: list) -> list:
    """
    Operador INVERSIÓN: selecciona un bloque de inicio y longitud
    variables dentro del cromosoma y lo invierte.

    Equivale al movimiento 2-opt clásico en TSP; es especialmente
    útil para eliminar bucles en el recorrido del agente viajero.
    """
    i = random.randint(0, N - 2)
    j = random.randint(i + 1, N - 1)
    child = route[:]
    child[i:j + 1] = list(reversed(child[i:j + 1]))
    return child


def reproduce(parent_chrom: list) -> list:
    """
    Paso 8: aplica pseudo-aleatoriamente enroque o inversión
    sobre la ruta decodificada y devuelve el hijo re-codificado.

    Decodificar → operar sobre la ruta → re-codificar garantiza
    que el cromosoma hijo sea siempre un ordinal válido.
    """
    route = decode(parent_chrom)
    if random.random() < 0.5:
        child_route = enroque(route)
    else:
        child_route = inversion(route)
    return encode(child_route)


# ══════════════════════════════════════════════════════════════
#  VISUALIZACIÓN — 2 ventanas en tiempo real (Paso 11)
# ══════════════════════════════════════════════════════════════

def setup_plots():
    """
    Inicializa las dos ventanas gráficas:
      Ventana 1 – Ruta del individuo más apto (actualizada por generación)
      Ventana 2 – Función de aptitud: distancia mínima vs. generación
    """
    plt.ion()

    # ── Ventana 1: Ruta ──────────────────────────────────────
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    try:
        fig1.canvas.manager.set_window_title('Ventana 1 — Ruta del Agente Viajero')
    except Exception:
        pass

    xs = [c[0] for c in CITIES]
    ys = [c[1] for c in CITIES]

    ax1.set_xlim(-0.5, 11.5)
    ax1.set_ylim(-0.5, 11.5)
    ax1.set_title('Ruta del individuo más apto', fontsize=12, fontweight='bold')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.grid(True, alpha=0.3)
    ax1.scatter(xs, ys, s=130, c='steelblue', zorder=5)

    for i, (x, y) in enumerate(CITIES):
        ax1.annotate(f'C{i+1}', (x, y),
                     textcoords='offset points', xytext=(5, 4),
                     fontsize=7, color='navy', fontweight='bold')

    route_line, = ax1.plot([], [], 'tomato', linewidth=1.8, alpha=0.85, zorder=4)

    dist_text = ax1.text(
        0.02, 0.97, '', transform=ax1.transAxes,
        fontsize=10, va='top', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                  edgecolor='goldenrod', alpha=0.9)
    )
    gen_text = ax1.text(
        0.02, 0.89, '', transform=ax1.transAxes,
        fontsize=9, va='top', color='dimgray'
    )

    try:
        fig1.canvas.manager.window.wm_geometry('+30+50')
    except Exception:
        pass

    # ── Ventana 2: Función de aptitud ────────────────────────
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    try:
        fig2.canvas.manager.set_window_title('Ventana 2 — Función de Aptitud')
    except Exception:
        pass

    ax2.set_title('Distancia mínima por generación', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Generación')
    ax2.set_ylabel('Distancia del mejor individuo')
    ax2.set_xlim(0, GENERATIONS)
    ax2.grid(True, alpha=0.3)

    fitness_line, = ax2.plot([], [], color='steelblue', linewidth=2)
    ax2.set_ylim(0, 1)   # se ajusta dinámicamente

    try:
        fig2.canvas.manager.window.wm_geometry('+720+50')
    except Exception:
        pass

    plt.pause(0.05)
    return (fig1, ax1, route_line, dist_text, gen_text,
            fig2, ax2, fitness_line)


def update_plots(ax1, route_line, dist_text, gen_text,
                 ax2, fitness_line,
                 route, distance, gen, history,
                 fig1, fig2):
    """Refresca ambas ventanas al terminar cada generación."""

    # Ventana 1 — actualizar ruta
    rxs = [CITIES[c][0] for c in route] + [CITIES[route[0]][0]]
    rys = [CITIES[c][1] for c in route] + [CITIES[route[0]][1]]
    route_line.set_data(rxs, rys)
    dist_text.set_text(f'Distancia: {distance:.4f}')
    gen_text.set_text(f'Generación: {gen}')

    # Ventana 2 — actualizar curva de aptitud
    gens = list(range(1, len(history) + 1))
    fitness_line.set_data(gens, history)
    ymin, ymax = min(history), max(history)
    margin = (ymax - ymin) * 0.1 + 0.5
    ax2.set_ylim(ymin - margin, ymax + margin)

    fig1.canvas.draw_idle()
    fig2.canvas.draw_idle()
    plt.pause(0.05)


# ══════════════════════════════════════════════════════════════
#  ALGORITMO GENÉTICO — BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════

def run():
    print('╔══════════════════════════════════════════════════════════╗')
    print('║   ALGORITMO GENÉTICO ORDINAL — TSP  │  UAG · IA          ║')
    print('╚══════════════════════════════════════════════════════════╝\n')
    print(f'  Ciudades            : {N}')
    print(f'  Tamaño de población : {POP_SIZE}')
    print(f'  Generaciones        : {GENERATIONS}')
    print(f'  Torneo              : {TOURNAMENT_SIZE} candidatos '
          f'({TOURNAMENT_SIZE / POP_SIZE * 100:.0f}% de la población)')
    print( '  Reproducción        : Enroque / Inversión (50 % / 50 %)')
    print( '  Codificación        : Ordinal')
    print( '  Visualización       : 2 ventanas en tiempo real\n')
    print('─' * 62)

    # ── Inicializar gráficas ──────────────────────────────────
    (fig1, ax1, route_line, dist_text, gen_text,
     fig2, ax2, fitness_line) = setup_plots()

    # ── Paso 1: Población inicial ─────────────────────────────
    population = initialize_population()

    # ── Pasos 2-3: Evaluar aptitud inicial ────────────────────
    fitnesses  = [fitness(c) for c in population]

    best_idx   = min(range(POP_SIZE), key=lambda i: fitnesses[i])
    best_chrom = population[best_idx][:]
    best_dist  = fitnesses[best_idx]
    history    = []

    # ── Paso 4: Ciclo for principal — 100 generaciones ────────
    for gen in range(1, GENERATIONS + 1):

        # ── Pasos 5-9: 100 torneos → 100 hijos ───────────────
        children = []
        for _ in range(POP_SIZE):
            parent = tournament_select(population, fitnesses)   # paso 6-7
            child  = reproduce(parent)                          # paso 8-9
            children.append(child)

        # ── Paso 10: Reemplazar población con hijos ───────────
        population = children
        fitnesses  = [fitness(c) for c in population]

        # Actualizar mejor global
        min_fit = min(fitnesses)
        min_idx = fitnesses.index(min_fit)
        if min_fit < best_dist:
            best_dist  = min_fit
            best_chrom = population[min_idx][:]

        history.append(best_dist)

        # ── Paso 11: Graficar ruta y función de aptitud ───────
        best_route = decode(best_chrom)
        update_plots(ax1, route_line, dist_text, gen_text,
                     ax2, fitness_line,
                     best_route, best_dist, gen, history,
                     fig1, fig2)

        print(f'  Gen {gen:>3d} │ Mejor distancia = {best_dist:>10.4f}')

    # ── Paso 12: Cerrar ciclo for ─────────────────────────────
    print('─' * 62)
    print('\n╔══════════════════════════════════════════════════════════╗')
    print('║                    RESULTADO FINAL                       ║')
    print('╚══════════════════════════════════════════════════════════╝')
    print(f'\n  Mejor distancia encontrada : {best_dist:.4f}')
    print(f'  Distancia inicial (gen 1)  : {history[0]:.4f}')
    improvement = (history[0] - best_dist) / history[0] * 100
    print(f'  Mejora total               : {improvement:.1f}%')
    best_route = decode(best_chrom)
    ruta_str   = ' → '.join(f'C{c + 1}' for c in best_route)
    print(f'\n  Ruta óptima encontrada:')
    print(f'    {ruta_str} → C{best_route[0] + 1}\n')

    plt.ioff()
    plt.show()   # mantiene las ventanas abiertas al terminar


if __name__ == '__main__':
    run()
