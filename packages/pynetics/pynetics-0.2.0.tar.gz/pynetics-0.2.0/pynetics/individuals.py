import abc

from pynetics.fitnesses import Fitness
from pynetics.utils import check_is_instance_of


class Individual:
    """ One of the possible solutions to a problem.

    In a genetic algorithm, an individual is a tentative solution of a problem,
    i.e. the environment where populations of individuals evolve.
    """

    def __init__(self, disable_cache=False):
        """ Initializes the individual. """
        self.disable_cache = disable_cache
        self.population = None
        self.f_fitness = None
        self.__cache_fitness = None

    def fitness(self, init=False):
        """ Computes the fitness of this individual.

        It will use the fitness method defined on its spawning pool.

        :param init: If this call to fitness is in initialization time. It
            defaults to False.
        :return: A fitness.
        """
        if self.disable_cache or (not self.__cache_fitness and init):
            return self.f_fitness(self, init)
        elif not self.__cache_fitness:
            self.__cache_fitness = self.f_fitness(self, init)
        return self.__cache_fitness

    @abc.abstractmethod
    def phenotype(self):
        """ The expression of this particular individual in the environment.

        :return: An object representing this individual in the environment
        """


class SpawningPool(metaclass=abc.ABCMeta):
    """ Defines the methods for creating individuals required by population. """

    def __init__(self, fitness):
        """ Initializes this spawning pool.

        :param fitness: The method to evaluate individuals.
        """
        self.population = None
        self.fitness = check_is_instance_of(fitness, Fitness)

    def spawn(self):
        """ Returns a new random individual.

        It uses the abstract method "create" to be implemented with the logic
        of individual creation. The purpose of this method is to add the
        parameters the base individual needs.

        :return: An individual instance.
        """
        individual = self.create()
        individual.population = self.population
        individual.f_fitness = self.fitness
        return individual

    @abc.abstractmethod
    def create(self):
        """ Creates a new individual randomly.

        :return: A new Individual object.
        """
