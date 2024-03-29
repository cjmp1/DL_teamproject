import copy
from datetime import datetime
from typing import Callable

import numpy as np

from ga.individual import statistics
from util.timing import timing

import matplotlib.pyplot as plt

class Population:
    def __init__(self, individual, pop_size, max_generation, p_mutation, p_crossover, p_inversion):
        self.pop_size = pop_size
        self.max_generation = max_generation
        self.p_mutation = p_mutation
        self.p_crossover = p_crossover
        self.p_inversion = p_inversion
        self.old_population = [individual for _ in range(pop_size)]
        self.new_population = [individual for _ in range(pop_size)]

    @timing
    def run(self, env, run_generation: Callable, verbose=True, log=True, output_folder=None):
        print('hello')
        minfit_ = []
        maxfit_ = []
        for i in range(self.max_generation):
            c = 0
            max_fit = -1.0
            min_fit = 10000
            for p in self.old_population:
                p.calculate_fitness(env)
                print(p.fitness)
                if min_fit > p.fitness:
                    min_fit = p.fitness
                if max_fit < p.fitness:
                    max_fit = p.fitness
                print(c)
                c += 1
            print(min_fit, max_fit)
            minfit_.append(min_fit)
            maxfit_.append(max_fit)
            print(i, 'start')
            #self.new_population = []
            run_generation(env,
                           self.old_population,
                           self.new_population,
                           self.p_mutation,
                           self.p_crossover)


            if log:
                self.save_logs(i, output_folder)

            if verbose:
                self.show_stats(i)

            self.update_old_population()
            print(i, 'end')
            # TODO:
            #  save model every 1 / 10 of max generation ?

        self.save_model_parameters(output_folder)
        print(minfit_)
        print(maxfit_)
        plt.figure()
        plt.plot(minfit_,'r')
        plt.plot(maxfit_,'b')

    def save_logs(self, n_gen, output_folder):
        """
        CSV format -> date,n_generation,mean,min,max
        """
        date = self.now()
        file_name = 'logs.csv'
        mean, min, max = statistics(self.new_population)
        stats = f'{date},{n_gen},{mean},{min},{max}\n'
        with open(output_folder + file_name, 'a') as f:
            f.write(stats)

    def show_stats(self, n_gen):
        mean, min, max = statistics(self.new_population)
        date = self.now()
        stats = f"{date} - generation {n_gen + 1} | mean: {mean}\tmin: {min}\tmax: {max}\n"
        print('hello')
        print(stats)

    def update_old_population(self):
        self.old_population = copy.deepcopy(self.new_population)

    def save_model_parameters(self, output_folder):
        best_model = self.get_best_model_parameters()
        date = self.now()
        file_name = self.get_file_name(date) + '.npy'
        np.save(output_folder + file_name, best_model)

    def get_best_model_parameters(self) -> np.array:
        """
        :return: Weights and biases of the best individual
        """
        individual = sorted(self.new_population, key=lambda ind: ind.fitness, reverse=True)[0]
        return individual.weights_biases

    def get_file_name(self, date):
        return '{}_NN={}_POPSIZE={}_GEN={}_PMUTATION_{}_PCROSSOVER_{}'.format(date,
                                                                              self.new_population[0].__class__.__name__,
                                                                              self.pop_size,
                                                                              self.max_generation,
                                                                              self.p_mutation,
                                                                              self.p_crossover)

    @staticmethod
    def now():
        return datetime.now().strftime('%m-%d-%Y_%H-%M')