#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 28 2026
@author: Arturo Olvera
------------------------------------------------------
Description:
Algoritmo Genetico Ordinal para el Problema del Agente
Viajero (TSP). Asignacion 1 - Inteligencia Artificial - UAG.

Parametros:
    Ciudades     : 20
    Poblacion    : 100 cromosomas
    Generaciones : 100
    Torneo       : 5 candidatos (5% de la poblacion)
    Reproduccion : Enroque / Inversion (50% / 50%)
    Codificacion : Ordinal
------------------------------------------------------
"""

import math
import random
import matplotlib.pyplot as plt          # type: ignore
import matplotlib.patches as mpatches   # type: ignore
from matplotlib.patches import Ellipse, Polygon  # type: ignore


# Coordenadas (x, y) de las 20 ciudades en el plano cartesiano
# Etiqueta visual: C1..C20 | Indice interno: 0..19
CITIES = [
    ( 1,  3), ( 3,  1), ( 5,  2), ( 7,  1), ( 9,  3),
    (10,  5), ( 9,  7), ( 7,  9), ( 5, 10), ( 3,  9),
    ( 1,  7), ( 2,  5), ( 4,  4), ( 6,  3), ( 8,  5),
    ( 7,  7), ( 5,  6), ( 3,  6), ( 4,  8), ( 6,  8),
]

N               = len(CITIES)   # 20 ciudades
POP_SIZE        = 100           # individuos por generacion
GENERATIONS     = 100           # iteraciones del ciclo principal
TOURNAMENT_SIZE = 5             # 5% de la poblacion
SEED            = 42

random.seed(SEED)


# ----------------------------------------------------------
# CODIFICACION ORDINAL
# ----------------------------------------------------------

def encode(route):
    "Convierte una permutacion (ruta) a cromosoma ordinal"
    ref = list(range(N))
    chrom = []
    for city in route:
        idx = ref.index(city)
        chrom.append(idx)
        ref.pop(idx)
    return chrom


def decode(chrom):
    "Convierte un cromosoma ordinal a permutacion (ruta)"
    ref = list(range(N))
    route = []
    for gene in chrom:
        idx = min(gene, len(ref) - 1)
        route.append(ref[idx])
        ref.pop(idx)
    return route


# ----------------------------------------------------------
# FUNCION DE FITNESS (aptitud)
# ----------------------------------------------------------

def euclidean(a, b):
    "Distancia euclidiana entre las ciudades a y b"
    dx = CITIES[a][0] - CITIES[b][0]
    dy = CITIES[a][1] - CITIES[b][1]
    return math.sqrt(dx * dx + dy * dy)


def route_distance(route):
    "Distancia total del recorrido circular"
    return sum(euclidean(route[i], route[(i + 1) % N]) for i in range(N))


def fitness(chrom):
    "Aptitud de un cromosoma: distancia total de su ruta decodificada"
    return route_distance(decode(chrom))


# ----------------------------------------------------------
# INICIALIZACION DE LA POBLACION
# ----------------------------------------------------------

def random_chromosome():
    "Genera un cromosoma ordinal aleatorio valido. Gen i pertenece a [0, N-1-i]"
    return [random.randint(0, N - 1 - i) for i in range(N)]


def initialize_population():
    "Paso 1: Crear aleatoriamente 100 cromosomas de longitud 20"
    return [random_chromosome() for _ in range(POP_SIZE)]


# ----------------------------------------------------------
# SELECCION POR TORNEO
# ----------------------------------------------------------

def tournament_select(population, fitnesses):
    "Elige 5 candidatos al azar y devuelve el de menor distancia"
    indices = random.sample(range(POP_SIZE), TOURNAMENT_SIZE)
    winner  = min(indices, key=lambda i: fitnesses[i])
    return population[winner][:]


# ----------------------------------------------------------
# OPERADORES DE REPRODUCCION
# ----------------------------------------------------------

def enroque(route):
    "Intercambia dos bloques de igual longitud dentro de la ruta"
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


def inversion(route):
    "Invierte un segmento de la ruta (equivalente al movimiento 2-opt)"
    i = random.randint(0, N - 2)
    j = random.randint(i + 1, N - 1)
    child = route[:]
    child[i:j + 1] = list(reversed(child[i:j + 1]))
    return child


def reproduce(parent_chrom):
    "Aplica enroque o inversion (50/50) y devuelve el hijo re-codificado"
    route = decode(parent_chrom)
    if random.random() < 0.5:
        child_route = enroque(route)
    else:
        child_route = inversion(route)
    return encode(child_route)


# ----------------------------------------------------------
# VISUALIZACION: 2 ventanas en tiempo real
# ----------------------------------------------------------

def setup_plots():
    "Inicializa las dos ventanas graficas"
    plt.ion()

    # Ventana 1: Ruta del agente viajero
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    try:
        fig1.canvas.manager.set_window_title('Ventana 1 - Ruta del Agente Viajero')
    except Exception:
        pass

    ax1.set_xlim(-0.5, 11.5)
    ax1.set_ylim(-0.5, 11.5)
    ax1.set_title('Ruta del individuo mas apto')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.grid(True, alpha=0.3)
    ax1.scatter([c[0] for c in CITIES], [c[1] for c in CITIES],
                s=130, c='steelblue', zorder=5)

    for i, (x, y) in enumerate(CITIES):
        ax1.annotate('C%d' % (i + 1), (x, y),
                     textcoords='offset points', xytext=(5, 4),
                     fontsize=7, color='navy', fontweight='bold')

    route_line, = ax1.plot([], [], 'tomato', linewidth=1.8, alpha=0.85, zorder=4)
    dist_text   = ax1.text(0.02, 0.97, '', transform=ax1.transAxes,
                           fontsize=10, va='top', fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3',
                                     facecolor='lightyellow', edgecolor='goldenrod'))
    gen_text    = ax1.text(0.02, 0.89, '', transform=ax1.transAxes,
                           fontsize=9, va='top', color='dimgray')

    try:
        fig1.canvas.manager.window.wm_geometry('+30+50')
    except Exception:
        pass

    # Ventana 2: Funcion de aptitud por generacion
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    try:
        fig2.canvas.manager.set_window_title('Ventana 2 - Funcion de Aptitud')
    except Exception:
        pass

    ax2.set_title('Distancia minima por generacion')
    ax2.set_xlabel('Generacion')
    ax2.set_ylabel('Distancia del mejor individuo')
    ax2.set_xlim(0, GENERATIONS)
    ax2.grid(True, alpha=0.3)

    fitness_line, = ax2.plot([], [], color='steelblue', linewidth=2)
    ax2.set_ylim(0, 1)

    try:
        fig2.canvas.manager.window.wm_geometry('+720+50')
    except Exception:
        pass

    plt.pause(0.15)
    return fig1, ax1, route_line, dist_text, gen_text, fig2, ax2, fitness_line


def update_plots(ax1, route_line, dist_text, gen_text,
                 ax2, fitness_line, route, distance, gen, history, fig1, fig2):
    "Refresca las dos ventanas al terminar cada generacion"

    rxs = [CITIES[c][0] for c in route] + [CITIES[route[0]][0]]
    rys = [CITIES[c][1] for c in route] + [CITIES[route[0]][1]]
    route_line.set_data(rxs, rys)
    dist_text.set_text('Distancia: %.4f' % distance)
    gen_text.set_text('Generacion: %d' % gen)

    gens = list(range(1, len(history) + 1))
    fitness_line.set_data(gens, history)
    ymin, ymax = min(history), max(history)
    margin = (ymax - ymin) * 0.1 + 0.5
    ax2.set_ylim(ymin - margin, ymax + margin)

    fig1.canvas.draw_idle()
    fig2.canvas.draw_idle()
    plt.pause(0.15)


# ----------------------------------------------------------
# DIAGRAMA DE FLUJO ANIMADO (Ventana 3)
# ----------------------------------------------------------

# Nodos del diagrama: (clave, etiqueta, x_centro, y_centro, forma, color_fondo, color_borde, color_texto)
_FLOW_NODES = [
    ('inicio',       'INICIO',                 5, 21.0, 'oval',    '#1d4ed8', '#1e3a8a', 'white'   ),
    ('params',       'Inicializar parametros', 5, 19.3, 'rect',    '#ede9fe', '#7c3aed', '#4c1d95' ),
    ('setup',        'setup_plots()',          5, 17.6, 'rect',    '#ede9fe', '#7c3aed', '#4c1d95' ),
    ('pausa',        'Pausa interactiva',      5, 15.9, 'rect',    '#fef9c3', '#ca8a04', '#713f12' ),
    ('poblacion',    'Poblacion inicial',      5, 14.2, 'rect',    '#ede9fe', '#7c3aed', '#4c1d95' ),
    ('evaluar',      'Evaluar fitness',        5, 12.5, 'rect',    '#fef3c7', '#f59e0b', '#92400e' ),
    ('actualizar',   'Actualizar mejor',       5, 10.8, 'rect',    '#fef3c7', '#f59e0b', '#92400e' ),
    ('check_gen',    'gen < 100?',             5,  9.1, 'diamond', '#dbeafe', '#3b82f6', '#1e40af' ),
    ('torneo',       'Torneo (x100)',          5,  7.4, 'rect',    '#dcfce7', '#16a34a', '#14532d' ),
    ('reproduccion', 'Enroque / Inversion',    5,  5.7, 'rect',    '#dcfce7', '#16a34a', '#14532d' ),
    ('encode',       'encode() -> hijo',       5,  4.0, 'rect',    '#dcfce7', '#16a34a', '#14532d' ),
    ('check_hijos',  '100 hijos?',             5,  2.3, 'diamond', '#dbeafe', '#3b82f6', '#1e40af' ),
    ('reemplazar',   'Reemplazar + Graficar',  5,  0.7, 'rect',    '#dcfce7', '#16a34a', '#14532d' ),
    ('fin',          'FIN',                    5, -0.9, 'oval',    '#1d4ed8', '#1e3a8a', 'white'   ),
]

# Coordenadas centrales de cada nodo para posicionar la bandera
_CENTERS = {node[0]: (node[2], node[3]) for node in _FLOW_NODES}

# Estado global del diagrama animado
_fd = {'fig': None, 'patches': {}, 'orig_ec': {}, 'orig_lw': {}, 'flag': None, 'prev': None}

# Colores de resaltado para el nodo activo
_HL_EC = '#f97316'   # naranja brillante
_HL_LW = 3.0
_NRM_LW = 1.5


def setup_flowchart():
    "Crea la Ventana 3 con el diagrama de flujo animado"
    fig3, ax3 = plt.subplots(figsize=(3.8, 11))
    try:
        fig3.canvas.manager.set_window_title('Ventana 3 - Diagrama de Flujo')
        fig3.canvas.manager.window.wm_geometry('+1380+30')
    except Exception:
        pass

    ax3.set_xlim(0.5, 9.5)
    ax3.set_ylim(-2.0, 22.5)
    ax3.axis('off')
    ax3.set_title('Flujo de ejecucion', fontsize=9, fontweight='bold', pad=3)

    RW = 4.2   # ancho de los rectangulos
    RH = 0.85  # alto de los rectangulos
    DX = 2.1   # semi-ancho del diamante
    DY = 0.62  # semi-alto del diamante

    for key, label, xc, yc, shape, fc, ec, tc in _FLOW_NODES:
        if shape == 'oval':
            p = Ellipse((xc, yc), width=3.4, height=RH + 0.15,
                        facecolor=fc, edgecolor=ec, linewidth=_NRM_LW, zorder=3)
            ax3.add_patch(p)
            ax3.text(xc, yc, label, ha='center', va='center',
                     fontsize=8.5, fontweight='bold', color=tc, zorder=4)

        elif shape == 'diamond':
            pts = [(xc, yc + DY), (xc + DX, yc), (xc, yc - DY), (xc - DX, yc)]
            p = Polygon(pts, closed=True,
                        facecolor=fc, edgecolor=ec, linewidth=_NRM_LW, zorder=3)
            ax3.add_patch(p)
            ax3.text(xc, yc, label, ha='center', va='center',
                     fontsize=7.5, fontweight='600', color=tc, zorder=4)

        else:
            p = mpatches.FancyBboxPatch(
                (xc - RW / 2, yc - RH / 2), RW, RH,
                boxstyle='round,pad=0.07',
                facecolor=fc, edgecolor=ec, linewidth=_NRM_LW, zorder=3
            )
            ax3.add_patch(p)
            ax3.text(xc, yc, label, ha='center', va='center',
                     fontsize=8, fontweight='600', color=tc, zorder=4)

        _fd['patches'][key] = p
        _fd['orig_ec'][key] = ec
        _fd['orig_lw'][key] = _NRM_LW

    # Flechas entre nodos consecutivos
    gaps = [
        (21.0, 'oval',    19.3, 'rect'),
        (19.3, 'rect',    17.6, 'rect'),
        (17.6, 'rect',    15.9, 'rect'),
        (15.9, 'rect',    14.2, 'rect'),
        (14.2, 'rect',    12.5, 'rect'),
        (12.5, 'rect',    10.8, 'rect'),
        (10.8, 'rect',     9.1, 'diamond'),
        ( 9.1, 'diamond',  7.4, 'rect'),
        ( 7.4, 'rect',     5.7, 'rect'),
        ( 5.7, 'rect',     4.0, 'rect'),
        ( 4.0, 'rect',     2.3, 'diamond'),
        ( 2.3, 'diamond',  0.7, 'rect'),
        ( 0.7, 'rect',    -0.9, 'oval'),
    ]

    def bot(yc, shape):
        "Punto inferior del nodo"
        if shape == 'oval':    return yc - (RH + 0.15) / 2
        if shape == 'diamond': return yc - DY
        return yc - RH / 2

    def top(yc, shape):
        "Punto superior del nodo"
        if shape == 'oval':    return yc + (RH + 0.15) / 2
        if shape == 'diamond': return yc + DY
        return yc + RH / 2

    for y1, s1, y2, s2 in gaps:
        ay = bot(y1, s1) - 0.05
        by = top(y2, s2) + 0.05
        ax3.annotate('', xy=(5, by), xytext=(5, ay),
                     arrowprops=dict(arrowstyle='->', color='#9ca3af', lw=1.1))

    # Flecha de retorno: reemplazar (y=0.7) -> evaluar (y=12.5) por la izquierda
    loop_x = 1.0
    ax3.plot([5 - RW / 2, loop_x], [0.7,  0.7],  color='#9ca3af', lw=1.1)
    ax3.plot([loop_x,     loop_x], [0.7, 12.5],   color='#9ca3af', lw=1.1)
    ax3.annotate('', xy=(5 - RW / 2, 12.5), xytext=(loop_x, 12.5),
                 arrowprops=dict(arrowstyle='->', color='#9ca3af', lw=1.1))
    ax3.text(loop_x - 0.25, 6.6, 'sig. gen.', fontsize=6.5, color='#9ca3af',
             rotation=90, va='center', ha='center')

    # Flecha NO de check_gen: hacia fin por la derecha
    ax3.plot([5 + DX, 8.5], [9.1, 9.1],  color='#ef4444', lw=1.1)
    ax3.plot([8.5,    8.5], [9.1, -0.9], color='#ef4444', lw=1.1)
    ax3.annotate('', xy=(5 + 3.4 / 2, -0.9), xytext=(8.5, -0.9),
                 arrowprops=dict(arrowstyle='->', color='#ef4444', lw=1.1))
    ax3.text(8.8, 4.0, 'NO', fontsize=6.5, color='#ef4444', rotation=90, va='center')

    # Bandera: triangulo rojo a la izquierda del nodo activo
    flag_obj, = ax3.plot([], [], marker='>', ms=11, color='#ef4444',
                         linestyle='none', zorder=7)
    _fd['flag'] = flag_obj
    _fd['fig']  = fig3

    fig3.tight_layout(pad=0.4)
    plt.pause(0.1)
    return fig3


def highlight_step(key, pause=0.0):
    "Mueve la bandera al nodo activo y resalta su borde"
    patches = _fd['patches']
    prev    = _fd['prev']
    flag    = _fd['flag']
    fig3    = _fd['fig']

    # Restaurar nodo anterior
    if prev and prev in patches:
        patches[prev].set_edgecolor(_fd['orig_ec'][prev])
        patches[prev].set_linewidth(_fd['orig_lw'][prev])

    # Resaltar nodo actual
    if key in patches:
        patches[key].set_edgecolor(_HL_EC)
        patches[key].set_linewidth(_HL_LW)
        xc, yc = _CENTERS[key]
        flag.set_data([xc - 2.6], [yc])

    _fd['prev'] = key
    fig3.canvas.draw_idle()
    if pause > 0:
        plt.pause(pause)


# ----------------------------------------------------------
# ALGORITMO GENETICO PRINCIPAL
# ----------------------------------------------------------

def run():
    "Ejecuta el algoritmo genetico completo para el TSP"

    print('Algoritmo Genetico Ordinal - TSP')
    print('Ciudades: %d | Poblacion: %d | Generaciones: %d' % (N, POP_SIZE, GENERATIONS))
    print('-' * 50)

    # Ventana 3: diagrama de flujo (se abre primero para que sea visible desde el inicio)
    setup_flowchart()
    highlight_step('inicio', pause=0.7)
    highlight_step('params', pause=0.6)
    highlight_step('setup',  pause=0.5)

    # Ventanas 1 y 2
    fig1, ax1, route_line, dist_text, gen_text, fig2, ax2, fitness_line = setup_plots()

    highlight_step('pausa', pause=0.3)
    print('')
    print('Acomoda las ventanas y presiona Enter para iniciar...')
    input()

    # Paso 1: Poblacion inicial
    highlight_step('poblacion', pause=0.6)
    population = initialize_population()

    # Pasos 2-3: Evaluar aptitud inicial
    highlight_step('evaluar', pause=0.5)
    fitnesses  = [fitness(c) for c in population]

    highlight_step('actualizar', pause=0.5)
    best_idx   = min(range(POP_SIZE), key=lambda i: fitnesses[i])
    best_chrom = population[best_idx][:]
    best_dist  = fitnesses[best_idx]
    history    = []

    # Paso 4: Ciclo for principal - 100 generaciones
    for gen in range(1, GENERATIONS + 1):

        highlight_step('check_gen')

        # Pasos 5-9: 100 torneos, un hijo por torneo
        highlight_step('torneo')
        highlight_step('reproduccion')
        highlight_step('encode')
        children = []
        for _ in range(POP_SIZE):
            parent = tournament_select(population, fitnesses)
            child  = reproduce(parent)
            children.append(child)

        highlight_step('check_hijos')

        # Paso 10: Reemplazar poblacion con hijos
        highlight_step('reemplazar')
        population = children
        fitnesses  = [fitness(c) for c in population]

        min_fit = min(fitnesses)
        min_idx = fitnesses.index(min_fit)
        if min_fit < best_dist:
            best_dist  = min_fit
            best_chrom = population[min_idx][:]

        history.append(best_dist)

        # Paso 11: Graficar ruta y funcion de aptitud
        best_route = decode(best_chrom)
        update_plots(ax1, route_line, dist_text, gen_text,
                     ax2, fitness_line,
                     best_route, best_dist, gen, history, fig1, fig2)

        # Actualizar diagrama de flujo tambien
        _fd['fig'].canvas.draw_idle()

        print('Gen %3d | Mejor distancia = %.4f' % (gen, best_dist))

    # Paso 12: Fin del ciclo
    highlight_step('fin', pause=0.5)
    print('-' * 50)
    print('Resultado final')
    print('Mejor distancia : %.4f' % best_dist)
    print('Distancia inicial: %.4f' % history[0])
    print('Mejora total    : %.1f%%' % ((history[0] - best_dist) / history[0] * 100))

    best_route = decode(best_chrom)
    ruta_str   = ' -> '.join('C%d' % (c + 1) for c in best_route)
    print('Ruta: %s -> C%d' % (ruta_str, best_route[0] + 1))

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    run()
