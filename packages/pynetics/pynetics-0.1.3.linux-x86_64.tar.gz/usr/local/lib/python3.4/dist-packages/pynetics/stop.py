import abc


class StopCondition(metaclass=abc.ABCMeta):
    """ A condition to be met in order to stop the algorithm.

    Although the stop condition is defined as a class, it's enough to provide a
    function that is able to discern whether the time has come to stop (True or
    False) receiving as parameter the population.
    """

    @abc.abstractmethod
    def __call__(self, genetic_algorithm):
        """ Checks if this stop condition is met.

        :param genetic_algorithm: The genetic algorithm where this stop
            condition belongs.
        :return: True if criteria is met, false otherwise.
        """


class StepsNumStopCondition(StopCondition):
    """ If the genetic algorithm has made enough iterations. """

    def __init__(self, steps):
        """ Initializes this function with the number of iterations.

        :param steps: An integer value.
        """
        self.steps = steps

    def __call__(self, genetic_algorithm):
        """ Checks if this stop criteria is met.

        It will look at the generation of the genetic algorithm. It's expected
        that. If its generation is greater or equal to the specified in
        initialization method, the criteria is met.

        :param genetic_algorithm: The genetic algorithm where this stop
            condition belongs.
        :return: True if criteria is met, false otherwise.
        """
        return genetic_algorithm.generation >= self.steps


class FitnessBound(StopCondition):
    """ If the genetic algorithm obtained a fine enough individual. """

    def __init__(self, fitness_bound, all_populations=False):
        """ Initializes this function with the upper bound for the fitness.

        :param fitness_bound: An fitness value.
        :param all_populations: If True, the condition will be met only when all
            the populations contain at least one individual with a fitness
            higher than the bound. If False, only one individual among all the
            populations will suffice.
        """
        self.fitness_bound = fitness_bound
        self.all_populations = all_populations

    def __call__(self, genetic_algorithm):
        """ Checks if this stop criteria is met.

        It will look at the generation of the genetic algorithm. It's expected
        that. If its generation is greater or equal to the specified in
        initialization method, the criteria is met.

        :param genetic_algorithm: The genetic algorithm where this stop
            condition belongs.
        :return: True if criteria is met, false otherwise.
        """
        fitnesses = [p[0].fitness() for p in genetic_algorithm.populations]
        criteria = [fitness > self.fitness_bound for fitness in fitnesses]
        return all(criteria) if self.all_populations else any(criteria)
