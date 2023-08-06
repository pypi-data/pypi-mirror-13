import abc


class Fitness(metaclass=abc.ABCMeta):
    """ Method to estimate how adapted is the individual to the environment. """

    def __call__(self, individual, init=False):
        """ Calculates the fitness of the individual.

        This method does some checks and the delegates the computation of the
        fitness to the "perform" method.

        :param individual: The individual to which estimate the adaptation.
        :param init: If this call to fitness is in initialization time. It
            defaults to False.
        :return: A sortable object representing the adaptation of the individual
            to the environment.
        """
        if individual is None:
            raise ValueError('The individual cannot be None')
        elif init:
            return self.init_perform(individual)
        else:
            return self.perform(individual)

    def init_perform(self, individual):
        """ Estimates how adapted is the individual at initialization time.

        This is useful in schemas where the fitness while initializing is
        computed in a different way than along the generations.

        Overriding this method can be tricky, specially in a co-evolutionary
        scheme. In this stage of the algorithm (initialization) the populations
        are not sorted, and it's position on its population cannot depend on the
        best of other individuals of other populations (circular dependency).
        Therefore, calling other_population[0] is not an option here.

        The scheme proposed by Mitchell A. et. al. in "A Cooperative
        Coevolutionary Approach to Function Optimization", the initialization
        may be performed by selecting a random individual among the other
        populations instead the best. For this purpose, a random() method in
        Population class is provided.

        The default behavior is to call method "perform" but can be overridden
        to any other behavior if needed.

        :param individual: The individual to which estimate the adaptation.
        :return: A sortable object representing the adaptation of the individual
            to the environment.
        """
        try:
            return self.perform(individual)
        except AttributeError as e:
            # If genetic_algorithm property is not set at this moment, it's
            # probably because a co-evolution is being implemented and that an
            # init_perform implementation is required.
            msg = '{}. Maybe an init_perform implementation is needed'.format(e)
            raise AttributeError(msg)

    @abc.abstractmethod
    def perform(self, individual):
        """ Estimates how adapted is the individual.

        Must return something comparable (in order to be sorted with the results
        of the methods for other fitnesses). It's supposed that, the highest the
        fitness value is, the fittest the individual is in the environment.

        :param individual: The individual to which estimate the adaptation.
        :return: A sortable object representing the adaptation of the individual
            to the environment.
        """
