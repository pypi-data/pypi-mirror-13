import inspect
import math
from collections import abc

import random

from pynetics.catastrophe import Catastrophe
from pynetics.exceptions import WrongValueForInterval, NotAProbabilityError
from pynetics.fitnesses import Fitness
from pynetics.individuals import SpawningPool, Individual
from pynetics.mutation import Mutation, NoMutation
from pynetics.recombination import Recombination, NoRecombination
from pynetics.replacements import Replacement
from pynetics.selections import Selection
from pynetics.stop import StopCondition
from pynetics.utils import check_is_instance_of, take_chances

__version__ = '0.2.0'


class Population(abc.MutableSequence):
    """ Manages a population of individuals.

    A population is where individuals of the same kind evolve over an
    environment. A basic genetic algorithm consists in a single population, but
    more complex schemes involve two or more populations evolving concurrently.
    """

    def __init__(
        self,
        name=None,
        size=None,
        replacement_rate=None,
        spawning_pool=None,
        selection=None,
        recombination=None,
        p_recombination=None,
        mutation=None,
        p_mutation=None,
        replacement=None,
        individuals=None,
    ):
        """ Initializes the population, filling it with individuals.

        When the population is initialized, the fitness of the individuals
        generated is also calculated, implying that init_perform of every
        individual is called.

        Because operators requires to know which individual is the fittest,
        others which is the less fit and others need to travel along the
        collection of individuals in some way or another (e.g. from fittest to
        less fit), the population is always sorted when an access is required.
        Thus, writing population[0] always returns the fittest individual,
        population[1] the next and so on, until population[-1] which is the less
        fit.

        :param name: The name of this population.
        :param size: The size this population should have.
        :param replacement_rate: The rate of individuals to be replaced in each
            step of the algorithm. Must be a float value in the (0, 1] interval.
        :param spawning_pool: The object that generates individuals.
        :param selection: The method to select individuals of the population to
            recombine.
        :param recombination: The method to recombine parents in order to
            generate an offspring with characteristics of the parents. If none,
            no recombination will be applied.
        :param p_recombination: The odds for recombination method to be
            performed over a set of selected individuals to generate progeny. If
            not performed, progeny will be the parents. Must be a value between
            0 and 1 (both included).
        :param mutation: The method to mutate an individual. If none, no
            mutation over the individual will be applied.
        :param p_mutation: The odds for mutation method to be performed over a
            progeny. It's applied once for each individual. If not performed the
            individuals will not be modified. Must be a value between 0 and 1
            (both included).
        :param replacement: The method that will add and remove individuals from
            the population given the set of old individuals (i.e. the ones on
            the population before the evolution step) and new individuals (i.e.
            the offspring).
        :param individuals: The list of starting individuals. If none or if its
            length is lower than the population size, the rest of individuals
            will be generated randomly. If the length of initial individuals is
            greater than the population size, a random sample of the individuals
            is selected as members of population.
        :raises ValueError: If no name for this population is provided.
        :raises WrongValueForIntervalError: If any of the bounded values fall
            out of their respective intervals.
        :raises NotAProbabilityError: If a value was expected to be a
            probability and it wasn't.
        :raises UnexpectedClassError: If any of the instances provided wasn't
            of the required class.
        """
        if not name:
            raise ValueError('A name for population is required')
        if size is None or size < 1:
            raise WrongValueForInterval('size', 0, '∞', size, inc_lower=False)
        if replacement_rate is None or not 0 < replacement_rate <= 1:
            raise WrongValueForInterval(
                'replacement_rate',
                0,
                1,
                replacement_rate,
                inc_lower=False
            )
        if p_recombination is None or not 0 <= p_recombination <= 1:
            raise NotAProbabilityError('p_recombination', p_recombination)
        if p_mutation is None or not 0 <= p_mutation <= 1:
            raise NotAProbabilityError('p_mutation', p_mutation)

        self.name = name
        self.size = size
        self.replacement_rate = replacement_rate
        self.spawning_pool = check_is_instance_of(spawning_pool, SpawningPool)
        self.spawning_pool.population = self
        self.selection = check_is_instance_of(selection, Selection)
        self.recombination = check_is_instance_of(recombination, Recombination)
        self.p_recombination = p_recombination
        self.mutation = check_is_instance_of(mutation, Mutation)
        self.p_mutation = p_mutation
        self.replacement = check_is_instance_of(replacement, Replacement)

        self.individuals = individuals[:] if individuals else []
        while len(self.individuals) > self.size:
            self.individuals.remove(random.choice(self.individuals))
        while len(self.individuals) < self.size:
            self.individuals.append(self.spawning_pool.spawn())

        # Precomputed values to speed up the things a bit
        self.offspring_size = int(math.ceil(size * replacement_rate))
        self.selection_size = len(
            inspect.signature(recombination.perform).parameters
        )

        self.sorted = False
        self.genetic_algorithm = None
        self.sort(init=True)
        self.best_individuals_by_generation = [self[0]]

    def __len__(self):
        """ Returns the number fo individuals this population has. """
        return len(self.individuals)

    def __delitem__(self, i):
        """ Removes the ith individual from the population.

        The population will be sorted by its fitness before deleting.

        :param i: The ith individual to delete.
        """
        self.sort()
        del self.individuals[i]

    def __setitem__(self, i, individual):
        """ Puts the named individual in the ith position.

        This call will cause a new sorting of the individuals the next time an
        access is required. This means that is preferable to make all the
        inserts in the population at once instead doing interleaved readings and
        inserts.

        :param i: The position where to insert the individual.
        :param individual: The individual to be inserted.
        """
        self.sorted = False
        self.__setitem__(i, individual)
        individual.population = self

    def insert(self, i, individual):
        """ Ads a new element to the ith position of the population population.

        This call will cause a new sorting of the individuals the next time an
        access is required. This means that is preferable to make all the
        inserts in the population at once instead doing interleaved readings and
        inserts.

        :param individual: The individual to be inserted in the population
        """
        self.sorted = False
        individual.population = self
        self.individuals.insert(i, individual)

    def __getitem__(self, i):
        """ Returns the individual located on the ith position.

        The population will be sorted before accessing to the element so it's
        correct to assume that the individuals are arranged from fittest (i = 0)
        to least fit (n  len(populaton)).

        :param i: The index of the individual to retrieve.
        :return: The individual.
        """
        self.sort()
        return self.individuals[i]

    def sort(self, init=False):
        """ Sorts this population from best to worst individual.

        :param init: If enabled, the fitness to perform will be the implemented
            in "init_perform" of fitness subclass. Is not expected to be used
            other than in initialization time. Defaults to False.
        """
        if not self.sorted:
            self.individuals.sort(
                key=lambda i: i.fitness(init=init),
                reverse=True
            )
            self.sorted = True

    def evolve(self):
        """ A step of evolution is made on this population.

        That means that a full cycle of select-recombine-mutate-replace is
        performed, potentially modifying the individuals this population
        contains.
        """
        # First, we generate the offspring given population replacement rate.
        offspring = []
        while len(offspring) < self.offspring_size:
            # Selection
            parents = self.selection(self, self.selection_size)
            # Recombination
            if take_chances(self.p_recombination):
                progeny = self.recombination(*parents)
            else:
                progeny = parents
            individuals_who_fit = min(
                len(progeny),
                self.offspring_size - len(offspring)
            )
            progeny = random.sample(progeny, individuals_who_fit)
            # Mutation
            for individual in progeny:
                if take_chances(self.p_mutation):
                    self.mutation(individual)
            # Add progeny to the offspring
            offspring.extend(progeny)

        # Once offspring is generated, a replace step is performed
        self.replacement(self, offspring)

        # The best individual is extracted and stored just in case is needed
        self.store_best_individual()

    def store_best_individual(self):
        current_gen = self.genetic_algorithm.generation
        best_individual = self[0]

        if len(self.best_individuals_by_generation) > current_gen:
            self.best_individuals_by_generation[current_gen] = best_individual
        else:
            self.best_individuals_by_generation.append(best_individual)

    def best(self, g=None):
        """ Returns the best individual for the gth.

        :param g: The generation from where obtain the best individual. If not
            specified, the returned generation will be the last generation.
        :return: The best individual for that generation.
        """
        return self.best_individuals_by_generation[g or -1]
