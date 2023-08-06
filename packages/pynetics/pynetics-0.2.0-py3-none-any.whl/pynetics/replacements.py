import abc


class Replacement(metaclass=abc.ABCMeta):
    """ Replacement of individuals of the population. """

    def __init__(self, maintain_population_size=True):
        """ Initializes this replacement method.

        :param maintain_population_size: If the population, once applied
            the replacement method, must have the same number of individuals. It
            defaults to True.
        """
        self.maintain_population_size = maintain_population_size

    def __call__(self, population, offspring):
        """ Performs some checks before applying the replacement method.

        :param population: The population where make the replacement.
        :param offspring: The new population to use as replacement.
        :raises ValueError: If the number of individuals in population is lower
            than the number of individuals in the offspring.
        """
        pre_length = len(population)
        self.perform(population, offspring)
        if self.maintain_population_size and pre_length != len(population):
            raise ValueError('Population length not maintained after replacing')

    @abc.abstractmethod
    def perform(self, population, offspring):
        """ It makes the replacement according to the subclass implementation.

        It is recommended for perform method to return the same

        :param population: The population where make the replacement.
        :param offspring: The new population to use as replacement.
        """


class LowElitism(Replacement):
    """ Low elitism replacement.

    The method will replace the less fit individuals by the ones specified in
    the offspring. This makes this operator elitist, but at least not much.
    Moreover, if offspring size equals to the population size then it's a full
    replacement (i.e. a generational scheme).
    """

    def perform(self, population, offspring):
        """ Removes less fit individuals and then inserts the offspring.

        :param population: The population where make the replacement.
        :param offspring: The new population to use as replacement.
        """
        del population[-len(offspring):]
        population.extend(offspring)


class HighElitism(Replacement):
    """ Drops the less fit individuals among all (population plus offspring).

    The method will add all the individuals in the offspring to the population,
    removing afterwards those individuals less fit. This makes this operator
    highly elitist but if length os population and offspring are the same, the
    process will result in a full replacement, i.e. a generational scheme of
    replacement.
    """

    def perform(self, population, offspring):
        """ Inserts the offspring in the population and removes the less fit.

        :param population: The population where make the replacement.
        :param offspring: The new population to use as replacement.
        """
        population.extend(offspring)
        del population[-len(offspring):]
