from evo2 import Individual, Evolution, Selection
from evo_std import Mutation

import random
import math
import matplotlib.pyplot as plt
from tqdm import tqdm


random.seed(100)
# Best ever: 290

CITY_COUNT = 20
city_names = [str(i) for i in range(CITY_COUNT)]
city_positions = {name: (random.randint(0, 100), random.randint(0, 100)) for name in city_names}

distance_matrix = {}
for start_city in city_names:
    local_distances = {}

    for end_city in city_names:
        start = city_positions[start_city]
        end = city_positions[end_city]
        dist = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)

        local_distances[end_city] = dist

    distance_matrix[start_city] = local_distances


def fitness(solution):
    if len(solution.city_names) < 2:
        return 0

    distance = 0
    prev_city = solution.city_names[0]

    # Use a local variable to speed it up
    cached_distance_matrix = distance_matrix
    for next_city in solution.city_names[1:]:
        distance += cached_distance_matrix[prev_city][next_city]
        prev_city = next_city

    return -distance


class TSP(Individual):
    __slots__ = "city_names",

    def __init__(self):
        super(TSP, self).__init__()
        self.city_names = []

    def create(self, init_params):
        self.city_names = city_names.copy()
        random.shuffle(self.city_names)

    def pair(self, other, pair_params):
        offspring = TSP()

        if len(self.city_names) < 1:
            return offspring

        start_idx = random.randint(0, len(self.city_names) - 1)
        end_idx = min(len(self.city_names),
                      start_idx + random.randint(pair_params["min_gene_len"], pair_params["max_gene_len"]))

        offspring.city_names.extend(self.city_names[:start_idx])
        visited = set(self.city_names[:start_idx])

        gene_to_copy = other.city_names[start_idx:end_idx]
        if random.random() <= pair_params["reverse_chance"]:
            gene_to_copy = reversed(gene_to_copy)

        for city in gene_to_copy:
            if city in visited:
                for city in self.city_names[start_idx:]:
                    if city not in visited:
                        break

            offspring.city_names.append(city)
            visited.add(city)

        if end_idx == len(self.city_names):
            return offspring

        for city in self.city_names[end_idx:]:
            if city in visited:
                for city in self.city_names[start_idx:]:
                    if city not in visited:
                        break

            offspring.city_names.append(city)
            visited.add(city)

        return offspring

    def mutate(self, mutate_params):
        # Randomly reverse a segment of the gene
        start = random.randint(0, len(self.city_names))
        end = min(
            len(self.city_names),
            random.randint(mutate_params["min_reverse_len"], mutate_params["max_reverse_len"]))

        Mutation.reverse_gene(self.city_names, start, end)

        # Randomly swap two towns
        for i in range(random.randint(0, mutate_params["random_rate"])):
            Mutation.randomly_swap_gene(self.city_names)

        # Shift the gene => Change the start and end
        Mutation.shift_gene(
            self.city_names,
            random.randint(mutate_params["min_shift"], mutate_params["max_shift"]),
            inplace=True)


def visualise_route(solution, blocking=True):
    plt.clf()
    cities_x = [city_positions[name][0] for name in city_names]
    cities_y = [city_positions[name][1] for name in city_names]
    plt.scatter(x=cities_x, y=cities_y, s=500, zorder=1)

    if len(solution.city_names) < 2:
        return

    prev = solution.city_names[0]
    for name in solution.city_names[1:]:
        cities_x = city_positions[prev][0], city_positions[name][0]
        cities_y = city_positions[prev][1], city_positions[name][1]
        plt.plot(cities_x, cities_y, c="grey", zorder=0)
        prev = name

    if blocking:
        plt.show()
    else:
        plt.draw()
        plt.pause(0.001)


evo = Evolution(
    TSP,
    100,
    n_offsprings=50,
    pair_params={"min_gene_len": 1, "max_gene_len": 8, "reverse_chance": 0.5},
    mutate_params={"random_rate": 3, "min_reverse_len": 2, "max_reverse_len": 5, "min_shift": -2, "max_shift": 2},
    selection_method=Selection.fittest,
    fitness_func=fitness
)

# visualise_route(TSP())
# plt.show()

pre_optimisation = -fitness(evo.population.individuals[0])

#evo.evolve(500)

history = []
for i in tqdm(range(500)):
    best = evo.evolve()
    history.append(best[0].fitness)
    visualise_route(best[0], blocking=False)

visualise_route(best[0], blocking=False)
post_optimisation = -fitness(best[0])

print(round(pre_optimisation), round(post_optimisation))
print("Improvement:", (1 - post_optimisation / pre_optimisation) * 100, "%")

plt.show()

plt.clf()
plt.plot(list(range(len(history))), history)
plt.show()
