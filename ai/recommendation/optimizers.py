# ai/recommendation/optimizers.py
import numpy as np
from typing import Callable, List, Tuple, Any, Dict
import random
import logging

logger = logging.getLogger(__name__)

class BaseOptimizer:
    """Base class for optimization algorithms."""
    
    def optimize(self, objective: Callable, bounds: List[Tuple[float, float]], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

class GeneticOptimizer(BaseOptimizer):
    """
    Simple genetic algorithm for multi‑objective optimization.
    Can be used for departure time optimization or signal timing.
    """
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elitism: int = 2,
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism

    def optimize(
        self,
        objective: Callable,
        bounds: List[Tuple[float, float]],
        maximize: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run genetic algorithm.
        objective: function that takes a list of variables and returns a fitness value.
        bounds: list of (min, max) for each variable.
        maximize: if True, maximize fitness; else minimize.
        """
        dim = len(bounds)
        # Initialize population
        population = [
            [random.uniform(bounds[i][0], bounds[i][1]) for i in range(dim)]
            for _ in range(self.population_size)
        ]
        best_individual = None
        best_fitness = -float('inf') if maximize else float('inf')

        for gen in range(self.generations):
            # Evaluate fitness
            fitness = []
            for ind in population:
                try:
                    val = objective(ind)
                    fitness.append(val)
                except Exception as e:
                    logger.warning(f"Error evaluating objective: {e}")
                    fitness.append(-float('inf') if maximize else float('inf'))

            # Elitism
            sorted_indices = np.argsort(fitness) if maximize else np.argsort(-np.array(fitness))
            elite = [population[i] for i in sorted_indices[:self.elitism]]

            # Update best
            best_idx = sorted_indices[0]
            if maximize and fitness[best_idx] > best_fitness:
                best_fitness = fitness[best_idx]
                best_individual = population[best_idx].copy()
            elif not maximize and fitness[best_idx] < best_fitness:
                best_fitness = fitness[best_idx]
                best_individual = population[best_idx].copy()

            # Selection (tournament)
            new_population = elite.copy()
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population, fitness, maximize)
                parent2 = self._tournament_selection(population, fitness, maximize)
                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1.copy()
                # Mutation
                child = self._mutate(child, bounds)
                new_population.append(child)
            population = new_population

        return {
            "best_individual": best_individual,
            "best_fitness": best_fitness,
            "converged": gen == self.generations - 1,
        }

    def _tournament_selection(self, population, fitness, maximize, tournament_size=3):
        idx = random.sample(range(len(population)), tournament_size)
        if maximize:
            best = max(idx, key=lambda i: fitness[i])
        else:
            best = min(idx, key=lambda i: fitness[i])
        return population[best].copy()

    def _crossover(self, parent1, parent2):
        # Uniform crossover
        return [parent1[i] if random.random() < 0.5 else parent2[i] for i in range(len(parent1))]

    def _mutate(self, individual, bounds):
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                # Gaussian mutation
                std = (bounds[i][1] - bounds[i][0]) * 0.1
                individual[i] += random.gauss(0, std)
                individual[i] = max(bounds[i][0], min(bounds[i][1], individual[i]))
        return individual