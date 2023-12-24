import json
import math
import random


class ES:
    def __init__(self, config: json):
        self.config = config
        self.population = []
        self.generation = 0
        self.problem = config["problem"]
        self.interval = config["interval"]
        self.dimension = config["dimension"]
        self.population_size = config["population_size"]
        self.survival_selection = config["survival_selection"]
        self.offspring = []
        self.lambda_ = config["lambda"]
        self.recombination = config["recombination"]
        self.max_generation = config["max_generation"]
        self.mutation = config["mutation"]
        self.ps = 0
        self.k = config["k"]
        self.best = []
        self.avg = []
        self.population = self.initiate_population()

    def initiate_population(self):
        population = []
        interval_length = self.interval[1] - self.interval[0]
        for _ in range(self.population_size):
            idv = []
            sigma = []
            for _ in range(self.dimension):
                idv.append(random.random() * interval_length + self.interval[0])
                if self.mutation == "fixed":
                    sigma.append(1)
                else:
                    sigma.append(random.random())
            population.append([idv, sigma, self.evaluate(idv)])

        return population

    def evaluate(self, idv):
        if self.problem == "ackley":
            return self.ackley(idv)
        elif self.problem == "schwefel":
            return self.schwefel(idv)
        else:
            raise Exception("problem not found")

    def ackley(self, idv):
        a = 20
        b = 0.2
        c = 2 * 3.1415926
        d = len(idv)
        sum1 = 0
        sum2 = 0
        for i in range(d):
            sum1 += idv[i] ** 2
            sum2 += math.cos(c * idv[i])
        term1 = -a * math.exp(-b * math.sqrt(sum1 / d))
        term2 = -math.exp(sum2 / d)
        return term1 + term2 + a + math.exp(1)

    def schwefel(self, idv):
        sum = 0
        for i in range(len(idv)):
            sum += idv[i] * math.sin(math.sqrt(abs(idv[i])))
        return 418.9829 * len(idv) - sum

    def mutate(self, idv):
        tau = 1 / math.sqrt(2 * self.dimension)
        new_idv = []
        new_sigma = []
        # Mutate sigma first
        if self.mutation == "fixed":
            new_sigma = idv[1]
        elif self.mutation == "adaptive":
            for i in range(len(idv[1])):
                new_sigma.append(idv[1][i] * math.exp(tau * random.gauss(0, 1)))
        else:
            raise Exception("mutation not found")
        # Mutate idv
        for i in range(len(idv[0])):
            new_idv.append(idv[0][i] + random.gauss(0, new_sigma[i]))
        return [new_idv, new_sigma, self.evaluate(new_idv)]

    def recombination_local_discrete(self):
        parent1, parent2 = random.sample(self.population, 2)
        child = []
        sigma = []
        for i in range(self.dimension):
            if random.random() < 0.5:
                child.append(parent1[0][i])
                sigma.append(parent1[1][i])
            else:
                child.append(parent2[0][i])
                sigma.append(parent2[1][i])

        fitness = self.evaluate(child)
        if fitness > parent1[2] and fitness > parent2[2]:
            self.ps += 1
        return [child, sigma, fitness]

    def recombination_global_discrete(self):
        child = []
        sigma = []
        for i in range(self.dimension):
            parent1, parent2 = random.sample(self.population, 2)
            if random.random() < 0.5:
                child.append(parent1[0][i])
                sigma.append(parent1[1][i])
            else:
                child.append(parent2[0][i])
                sigma.append(parent2[1][i])
        parent1, parent2 = random.sample(self.population, 2)
        fitness = self.evaluate(child)
        if fitness > parent1[2] and fitness > parent2[2]:
            self.ps += 1
        return [child, sigma, fitness]

    def recombination_local_intermediate(self):
        parent1, parent2 = random.sample(self.population, 2)
        child = []
        sigma = []
        for i in range(self.dimension):
            child.append((parent1[0][i] + parent2[0][i]) / 2)
            sigma.append((parent1[1][i] + parent2[1][i]) / 2)
        fitness = self.evaluate(child)
        if fitness > parent1[2] and fitness > parent2[2]:
            ps += 1
        return [child, sigma, fitness]

    def recombination_global_intermediate(self):
        child = []
        sigma = []
        for i in range(self.dimension):
            parent1, parent2 = random.sample(self.population, 2)
            child.append((parent1[0][i] + parent2[0][i]) / 2)
            sigma.append((parent1[1][i] + parent2[1][i]) / 2)
        parent1, parent2 = random.sample(self.population, 2)
        fitness = self.evaluate(child)
        if fitness > parent1[2] and fitness > parent2[2]:
            ps += 1
        return [child, sigma, fitness]

    def survival(self):
        if self.survival_selection == "mu_plus_lambda":
            self.population.sort(key=lambda x: x[2])
            self.population = self.population[: int(self.population_size * 0.95)]
            self.offspring.sort(key=lambda x: x[2])
            self.population += self.offspring[: (int(self.population_size * 0.05))]

        elif self.survival_selection == "mu_comma_lambda":
            self.population = self.offspring
            self.population.sort(key=lambda x: x[2])
            self.population = self.population[: self.population_size]
        else:
            raise Exception("survival_selection not found")
        # Sort population by fitness in ascending order
        self.population.sort(key=lambda x: x[2])
        self.population = self.population[: self.population_size]
        self.offspring = []

    def evolve(self):
        self.ps = 0
        # Recombination
        for i in range(self.lambda_):
            if self.recombination == "local_discrete":
                self.offspring.append(self.recombination_local_discrete())
            elif self.recombination == "global_discrete":
                self.offspring.append(self.recombination_global_discrete())
            elif self.recombination == "local_intermediate":
                self.offspring.append(self.recombination_local_intermediate())
            elif self.recombination == "global_intermediate":
                self.offspring.append(self.recombination_global_intermediate())
            else:
                raise Exception("recombination not found")
        # Mutation
        for i in range(self.lambda_):
            self.offspring[i] = self.mutate(self.offspring[i])
            for j in range(self.dimension):
                self.offspring[i][1][j] = max(0.0001, self.offspring[i][1][j])
                self.offspring[i][1][j] = min(1, self.offspring[i][1][j])
        # Survival
        self.survival()
        # Record best and average fitness
        self.best.append(self.population[0][2])
        sum = 0
        for i in range(self.population_size):
            sum += self.population[i][2]
        self.avg.append(sum / self.population_size)
        self.generation += 1

    def run(self):
        while self.generation < self.max_generation:
            self.evolve()
            if self.generation % self.k == 0 and self.mutation == "adaptive":
                # c [0.8, 1]
                c = random.random() * 0.2 + 0.8
                if self.ps > self.lambda_ / 5:
                    for i in range(self.population_size):
                        for j in range(self.dimension):
                            self.population[i][1][j] = self.population[i][1][j] * c
                elif self.ps < self.lambda_ / 5:
                    for i in range(self.population_size):
                        for j in range(self.dimension):
                            self.population[i][1][j] = self.population[i][1][j] / c
