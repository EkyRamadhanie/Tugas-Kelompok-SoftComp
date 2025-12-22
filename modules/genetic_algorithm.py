# modules/genetic_algorithm.py

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from .journal_data import Road


@dataclass
class GAResult:
    best_chromosome: List[int]
    selected_roads: List[Road]
    total_cost: float
    budget_limit: float
    present_avg_pcr: float
    new_avg_pcr: float
    total_delta_pcr: float
    generations: int
    history: List[float]


class GeneticAlgorithm:
    """
    GA knapsack sederhana untuk memilih jalan yang akan diperbaiki.

    - Chromosome: list 0/1, panjang = jumlah jalan.
      1 = jalan diperbaiki, 0 = tidak.
    - Objective: memaksimalkan total kenaikan PCR jaringan
      dengan batasan total biaya <= budget_limit.
    """

    def __init__(
        self,
        roads: List[Road],
        budget_ratio: float = 1.0,        # 1.0 = 100% budget jurnal
        population_size: int = 50,
        generations: int = 200,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.02,
        elite_fraction: float = 0.1,
    ) -> None:
        self.roads = roads
        self.n = len(roads)

        self.total_required_budget = sum(r.cost for r in roads)
        self.budget_limit = self.total_required_budget * budget_ratio

        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = max(1, int(elite_fraction * population_size))

        self.present_avg_pcr = sum(r.present_pcr for r in roads) / self.n

    # ========================= GA CORE =========================

    def _random_chromosome(self) -> List[int]:
        # mulai dari solusi yang relatif hemat (lebih banyak 0)
        return [1 if random.random() < 0.3 else 0 for _ in range(self.n)]

    def _decode(self, chromosome: List[int]) -> Tuple[float, float]:
        """
        Mengembalikan (total_cost, total_delta_pcr)
        """
        total_cost = 0.0
        total_delta = 0.0

        for bit, road in zip(chromosome, self.roads):
            if bit:
                total_cost += road.cost
                delta = max(0.0, road.new_pcr - road.present_pcr)
                total_delta += delta

        return total_cost, total_delta

    def _fitness(self, chromosome: List[int]) -> float:
        total_cost, total_delta = self._decode(chromosome)

        if total_cost > self.budget_limit:
            # solusi over-budget dianggap sangat jelek
            return -1e9 - (total_cost - self.budget_limit)

        # semakin besar total_delta semakin baik
        return total_delta

    def _tournament_select(self, population: List[List[int]], k: int = 3) -> List[int]:
        candidates = random.sample(population, k)
        candidates.sort(key=self._fitness, reverse=True)
        return candidates[0][:]

    def _crossover(self, p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
        if random.random() > self.crossover_rate or self.n < 2:
            return p1[:], p2[:]

        point = random.randint(1, self.n - 1)
        c1 = p1[:point] + p2[point:]
        c2 = p2[:point] + p1[point:]
        return c1, c2

    def _mutate(self, chrom: List[int]) -> None:
        for i in range(self.n):
            if random.random() < self.mutation_rate:
                chrom[i] = 1 - chrom[i]

    # ========================= PUBLIC API ======================

    def run(self, seed: int | None = None) -> GAResult:
        if seed is not None:
            random.seed(seed)

        # inisialisasi populasi
        population = [self._random_chromosome() for _ in range(self.population_size)]

        history: List[float] = []
        best = max(population, key=self._fitness)
        best_fit = self._fitness(best)

        for gen in range(self.generations):
            # elitism: simpan beberapa individu terbaik
            population.sort(key=self._fitness, reverse=True)
            new_pop = population[: self.elite_size]

            # generate offspring
            while len(new_pop) < self.population_size:
                p1 = self._tournament_select(population)
                p2 = self._tournament_select(population)
                c1, c2 = self._crossover(p1, p2)
                self._mutate(c1)
                self._mutate(c2)
                new_pop.append(c1)
                if len(new_pop) < self.population_size:
                    new_pop.append(c2)

            population = new_pop

            # update best
            current_best = max(population, key=self._fitness)
            current_fit = self._fitness(current_best)
            if current_fit > best_fit:
                best_fit = current_fit
                best = current_best[:]

            history.append(best_fit)

        # decode solusi terbaik
        total_cost, total_delta = self._decode(best)
        selected_roads = [r for bit, r in zip(best, self.roads) if bit]

        new_avg_pcr = self.present_avg_pcr + (total_delta / self.n)

        return GAResult(
            best_chromosome=best,
            selected_roads=selected_roads,
            total_cost=total_cost,
            budget_limit=self.budget_limit,
            present_avg_pcr=self.present_avg_pcr,
            new_avg_pcr=new_avg_pcr,
            total_delta_pcr=total_delta,
            generations=self.generations,
            history=history,
        )

    # helper untuk ditampilkan di template / CLI
    @staticmethod
    def result_to_dict(result: GAResult) -> Dict[str, Any]:
        return {
            "budget_limit": result.budget_limit,
            "total_cost": result.total_cost,
            "present_avg_pcr": result.present_avg_pcr,
            "new_avg_pcr": result.new_avg_pcr,
            "total_delta_pcr": result.total_delta_pcr,
            "improvement_percent": (
                (result.new_avg_pcr - result.present_avg_pcr)
                / result.present_avg_pcr
                * 100.0
                if result.present_avg_pcr > 0
                else 0.0
            ),
            "selected": [
                {
                    "id": r.id,
                    "technique": r.technique,
                    "present_pcr": r.present_pcr,
                    "new_pcr": r.new_pcr,
                    "delta_pcr": max(0.0, r.new_pcr - r.present_pcr),
                    "cost": r.cost,
                }
                for r in result.selected_roads
            ],
        }
