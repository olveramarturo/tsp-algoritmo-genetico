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
import matplotlib.pyplot as plt  # type: ignore


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

    plt.pause(0.05)
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
    plt.pause(0.05)


# ----------------------------------------------------------
# ALGORITMO GENETICO PRINCIPAL
# ----------------------------------------------------------

def run():
    "Ejecuta el algoritmo genetico completo para el TSP"

    print('Algoritmo Genetico Ordinal - TSP')
    print('Ciudades: %d | Poblacion: %d | Generaciones: %d' % (N, POP_SIZE, GENERATIONS))
    print('-' * 50)

    fig1, ax1, route_line, dist_text, gen_text, fig2, ax2, fitness_line = setup_plots()

    # Paso 1: Poblacion inicial
    population = initialize_population()

    # Pasos 2-3: Evaluar aptitud inicial
    fitnesses  = [fitness(c) for c in population]

    best_idx   = min(range(POP_SIZE), key=lambda i: fitnesses[i])
    best_chrom = population[best_idx][:]
    best_dist  = fitnesses[best_idx]
    history    = []

    # Paso 4: Ciclo for principal - 100 generaciones
    for gen in range(1, GENERATIONS + 1):

        # Pasos 5-9: 100 torneos, un hijo por torneo
        children = []
        for _ in range(POP_SIZE):
            parent = tournament_select(population, fitnesses)
            child  = reproduce(parent)
            children.append(child)

        # Paso 10: Reemplazar poblacion con hijos
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

        print('Gen %3d | Mejor distancia = %.4f' % (gen, best_dist))

    # Paso 12: Cerrar ciclo for
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
