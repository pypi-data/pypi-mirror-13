import abc


class Individual:
    """ One of the possible solutions to a problem.

    In a genetic algorithm, an individual is a tentative solution of a problem,
    i.e. the environment where populations of individuals evolve.
    """

    def __init__(self):
        """ Initializes the individual. """
        self.population = None

    def fitness(self):
        """ Cumputes the fitness of this individual.

        It will use the fitness method defined on its population.

        :return: A fitness.
        """
        return self.population.fitness(self)

    @abc.abstractmethod
    def phenotype(self):
        """ The expression of this particular individual in the environment.

        :return: An object representing this individual in the environment
        """

class SpawningPool(metaclass=abc.ABCMeta):
    """ Defines the methods for creating individuals required by population. """

    @abc.abstractmethod
    def create(self):
        """ Creates a new individual randomly.

        :return: A new Individual object.
        """
