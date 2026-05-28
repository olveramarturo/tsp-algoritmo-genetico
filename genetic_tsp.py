"""
================================================================
  ALGORITMO GENÉTICO ORDINAL – PROBLEMA DEL AGENTE VIAJERO
  (TSP – Traveling Salesman Problem)
================================================================
  Asignación 1 · Inteligencia Artificial · UAG

  Codificación  : Ordinal
  Selección     : Torneo (k-torneo)
  Cruce         : Un punto (one-point crossover)
  Mutación      : Reinicio aleatorio de gen
  Reemplazo     : Elitismo + nueva generación
================================================================
"""

import math
import random
import time
from typing import List, Tuple


# ──────────────────────────────────────────────────────────────
#  CLASE PRINCIPAL
# ──────────────────────────────────────────────────────────────

class GeneticTSP:
    """Algoritmo genético con codificación ordinal para el TSP."""

    def __init__(
        self,
        cities: List[Tuple[float, float]],
        population_size: int = 200,
        generations: int = 1000,
        mutation_rate: float = 0.02,
        crossover_rate: float = 0.85,
        tournament_size: int = 5,
        elite_count: int = 2,
        log_interval: int = 100,
        seed: int | None = None,
    ):
        self.cities = cities
        self.n = len(cities)

        self.population_size = population_size
        self.generations     = generations
        self.mutation_rate   = mutation_rate
        self.crossover_rate  = crossover_rate
        self.tournament_size = tournament_size
        self.elite_count     = elite_count
        self.log_interval    = log_interval

        if seed is not None:
            random.seed(seed)

        self.population: List[List[int]] = []
        self.best_chromosome: List[int] = []
        self.best_fitness: float = float("inf")
        self.history: List[float] = []   # mejor distancia por generación

    # ── CODIFICACIÓN ORDINAL ───────────────────────────────────

    def encode(self, route: List[int]) -> List[int]:
        """
        Codifica una ruta (permutación) en cromosoma ordinal.

        Para cada ciudad en la ruta se localiza su posición dentro
        de la lista de referencia restante y ese índice se guarda
        como gen. Luego la ciudad se elimina de la lista.

        Ejemplo con ruta [2, 0, 3, 1] y 4 ciudades:
          ref=[0,1,2,3] → pos(2)=2 → gen 2, ref=[0,1,3]
          ref=[0,1,3]   → pos(0)=0 → gen 0, ref=[1,3]
          ref=[1,3]     → pos(3)=1 → gen 1, ref=[1]
          ref=[1]       → pos(1)=0 → gen 0
          Cromosoma = [2, 0, 1, 0]
        """
        ref = list(range(self.n))
        chromosome = []
        for city in route:
            idx = ref.index(city)
            chromosome.append(idx)
            ref.pop(idx)
        return chromosome

    def decode(self, chromosome: List[int]) -> List[int]:
        """
        Decodifica un cromosoma ordinal a una ruta (proceso inverso).

        Cada gen indica el índice en la lista de referencia restante
        desde donde se extrae la próxima ciudad.
        """
        ref = list(range(self.n))
        route = []
        for i, gene in enumerate(chromosome):
            idx = min(gene, len(ref) - 1)   # clamping de seguridad
            route.append(ref[idx])
            ref.pop(idx)
        return route

    # ── INICIALIZACIÓN ────────────────────────────────────────

    def _random_chromosome(self) -> List[int]:
        """
        Genera un cromosoma ordinal aleatorio válido.
        El gen i tiene rango [0, n-1-i].
        """
        return [random.randint(0, self.n - 1 - i) for i in range(self.n)]

    def _initialize_population(self) -> None:
        self.population = [self._random_chromosome()
                           for _ in range(self.population_size)]

    # ── FITNESS ───────────────────────────────────────────────

    def _euclidean(self, a: int, b: int) -> float:
        dx = self.cities[a][0] - self.cities[b][0]
        dy = self.cities[a][1] - self.cities[b][1]
        return math.sqrt(dx * dx + dy * dy)

    def route_distance(self, route: List[int]) -> float:
        """Distancia total de un recorrido circular."""
        return sum(
            self._euclidean(route[i], route[(i + 1) % self.n])
            for i in range(self.n)
        )

    def fitness(self, chromosome: List[int]) -> float:
        """Fitness de un cromosoma (menor distancia = mejor)."""
        return self.route_distance(self.decode(chromosome))

    # ── SELECCIÓN: Torneo ─────────────────────────────────────

    def _tournament_select(self, fitnesses: List[float]) -> List[int]:
        """
        Selección por torneo: elige k individuos al azar y devuelve
        el cromosoma con menor distancia.
        """
        indices = random.sample(range(self.population_size), self.tournament_size)
        best = min(indices, key=lambda i: fitnesses[i])
        return self.population[best][:]

    # ── CRUCE: Un punto ───────────────────────────────────────

    def _crossover(
        self, p1: List[int], p2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """
        Cruce de un punto entre dos padres.

        La codificación ordinal permite el cruce estándar sin producir
        rutas inválidas, ya que cada gen tiene su propio rango
        independiente [0, n-1-i].

        Después del cruce se aplica un módulo por seguridad para
        mantener la validez de cada gen.
        """
        if random.random() > self.crossover_rate:
            return p1[:], p2[:]

        point = random.randint(1, self.n - 2)
        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]

        # Garantizar validez ordinal: gen[i] ∈ [0, n-1-i]
        for i in range(self.n):
            max_val = self.n - 1 - i
            c1[i] = c1[i] % (max_val + 1)
            c2[i] = c2[i] % (max_val + 1)

        return c1, c2

    # ── MUTACIÓN: Reinicio aleatorio ──────────────────────────

    def _mutate(self, chromosome: List[int]) -> List[int]:
        """
        Mutación por reinicio: cada gen muta con probabilidad
        mutation_rate a un valor aleatorio válido en su rango.
        """
        mutant = chromosome[:]
        for i in range(self.n):
            if random.random() < self.mutation_rate:
                mutant[i] = random.randint(0, self.n - 1 - i)
        return mutant

    # ── BUCLE PRINCIPAL ───────────────────────────────────────

    def run(self) -> dict:
        """
        Ejecuta el algoritmo genético completo.

        Flujo por generación:
          1. Evaluar fitness de toda la población
          2. Actualizar mejor solución global
          3. Elitismo: copiar los mejores directamente
          4. Selección → Cruce → Mutación para completar nueva generación
          5. Reemplazar población

        Returns:
            dict con 'route', 'distance' e 'history'
        """
        print("Inicializando población…\n")
        self._initialize_population()
        start = time.perf_counter()

        for gen in range(self.generations):

            # 1. Evaluar fitness
            fitnesses = [self.fitness(c) for c in self.population]

            # 2. Actualizar mejor solución global
            min_fit = min(fitnesses)
            min_idx = fitnesses.index(min_fit)

            if min_fit < self.best_fitness:
                self.best_fitness    = min_fit
                self.best_chromosome = self.population[min_idx][:]

            self.history.append(self.best_fitness)

            # Log periódico
            if gen % self.log_interval == 0 or gen == self.generations - 1:
                avg = sum(fitnesses) / len(fitnesses)
                elapsed = time.perf_counter() - start
                print(
                    f"  Gen {gen:>4d} │ "
                    f"Mejor = {self.best_fitness:>10.2f}  │ "
                    f"Promedio = {avg:>10.2f}  │ "
                    f"Tiempo = {elapsed:>5.1f}s"
                )

            # 3. Elitismo: preservar los mejores individuos
            ranked = sorted(range(self.population_size), key=lambda i: fitnesses[i])
            new_pop = [self.population[i][:] for i in ranked[: self.elite_count]]

            # 4. Completar nueva generación
            while len(new_pop) < self.population_size:
                p1 = self._tournament_select(fitnesses)
                p2 = self._tournament_select(fitnesses)
                c1, c2 = self._crossover(p1, p2)
                new_pop.append(self._mutate(c1))
                if len(new_pop) < self.population_size:
                    new_pop.append(self._mutate(c2))

            # 5. Reemplazar población
            self.population = new_pop

        best_route = self.decode(self.best_chromosome)
        return {
            "route":    best_route,
            "distance": self.best_fitness,
            "history":  self.history,
        }


# ──────────────────────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────

def main() -> None:
    # 25 ciudades con coordenadas (x, y)
    # Subconjunto inspirado en instancias clásicas de benchmarking TSP
    cities = [
        (565, 575), ( 25, 185), (345, 750), (945, 685), (845, 655),
        (880, 660), ( 25, 230), (525,1000), (580,1175), (650,1130),
        (1605, 620),(1220, 580),(1465, 200),(1530,   5),(845, 680),
        (725, 370), (145, 665), (415, 635), (510, 875), (560, 365),
        (300, 465), (520, 585), (480, 415), (835, 625), (975, 580),
    ]

    params = dict(
        population_size = 200,
        generations     = 1000,
        mutation_rate   = 0.02,
        crossover_rate  = 0.85,
        tournament_size = 5,
        elite_count     = 2,
        log_interval    = 100,
        seed            = 42,
    )

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   ALGORITMO GENÉTICO ORDINAL — TSP  │  UAG · IA          ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    print(f"  Ciudades            : {len(cities)}")
    print(f"  Tamaño de población : {params['population_size']}")
    print(f"  Generaciones        : {params['generations']}")
    print(f"  Tasa de mutación    : {params['mutation_rate']}")
    print(f"  Tasa de cruce       : {params['crossover_rate']}")
    print(f"  Tamaño de torneo    : {params['tournament_size']}")
    print(f"  Élite               : {params['elite_count']} individuos")
    print(f"  Semilla aleatoria   : {params['seed']}")
    print(f"  Codificación        : Ordinal\n")
    print("─" * 62)

    ga = GeneticTSP(cities, **params)
    result = ga.run()

    improvement = (ga.history[0] - result["distance"]) / ga.history[0] * 100

    print("─" * 62)
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║                    RESULTADO FINAL                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  Mejor distancia encontrada : {result['distance']:.2f}")
    print(f"  Distancia inicial (gen 0)  : {ga.history[0]:.2f}")
    print(f"  Mejora total               : {improvement:.1f}%\n")
    print("  Ruta óptima encontrada:")
    route_str = " → ".join(f"C{c}" for c in result["route"])
    print(f"    {route_str} → C{result['route'][0]}\n")


if __name__ == "__main__":
    main()
