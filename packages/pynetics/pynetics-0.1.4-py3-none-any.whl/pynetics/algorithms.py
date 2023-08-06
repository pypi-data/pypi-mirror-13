from collections import defaultdict

from pynetics import Population
from pynetics.catastrophe import Catastrophe, NoCatastrophe
from pynetics.mutation import NoMutation
from pynetics.stop import StopCondition
from pynetics.utils import check_is_instance_of


class GeneticAlgorithm:
    """ Base class where the evolutionary algorithm works.

    More than one algorithm may exist so a base class is created for specify the
    contract required by the other classes to work properly.
    """
    MSG_PRE_INITIALIZE = 'PRE_INITIALIZE'
    MSG_POST_INITIALIZE = 'POST_INITIALIZE'
    MSG_ALGORITHM_STARTED = 'ALGORITHM_STARTED'
    MSG_ALGORITHM_FINISHED = 'ALGORITHM_FINISHED'
    MSG_STEP_STARTED = 'STEP_STARTED'
    MSG_STEP_FINISHED = 'STEP_FINISHED'

    def __init__(
        self,
        stop_condition,
        populations,
        catastrophe,
    ):
        """ Initializes the genetic algorithm with the defaults.

        The populations_desc param should follow certain rules in order to work
        in the way the genetic algorithm is intended:
        1.  The population size of each of the populations must be greater than
            or equal to 1. If not, there will be nothing to be evolved.
        2.  The replacement rate should be at least 1 (otherwise no individual
            will be replaced) and, at most, the population size (i.e. a total
            replacement also called generational scheme).
        3.  The spawning pool must be an instance of SpawningPool class (or any
            of their subclasses).
        4.  The fitness method must be an instance of FitnessMethod class (or
            any of its subclasses).

        :param stop_condition: The condition to be met in order to stop the
            genetic algorithm.
        :param populations: The populations to be evolved.
        :param catastrophe: The method to be used as catastrophe
            operation.
        :raises UnexpectedClassError: If any of the input variables doesn't
            follow the contract required (i.e. doesn't inherit from a predefined
            class).
        """
        self.__stop_condition = check_is_instance_of(
            stop_condition,
            StopCondition
        )
        self.populations = populations
        self.listeners = defaultdict(list)
        self.catastrophe = check_is_instance_of(catastrophe, Catastrophe)
        self.generation = 0

        for population in self.populations:
            population.genetic_algorithm = self

    def run(self):
        """ Runs the simulation.

        The process is as follows: initialize populations and, while the stop
        condition is not met, do a new evolve step. This process relies in the
        abstract method "step".
        """
        [f(self) for f in self.listeners[self.MSG_PRE_INITIALIZE]]
        self.__initialize()
        [f(self) for f in self.listeners[self.MSG_POST_INITIALIZE]]
        [f(self) for f in self.listeners[self.MSG_ALGORITHM_STARTED]]
        while not self.__stop_condition(self):
            [f(self) for f in self.listeners[self.MSG_STEP_STARTED]]
            for population in self.populations:
                population.evolve()
                self.catastrophe(population)
            self.generation += 1
            [f(self) for f in self.listeners[self.MSG_STEP_FINISHED]]
        [f(self) for f in self.listeners[self.MSG_ALGORITHM_FINISHED]]

    def __initialize(self):
        """ Called when starting the genetic algorithm to initialize it. """
        self.generation = 0

    def best(self):
        """ Returns the best individuals obtained until now.

        They will be returned as a dictionary where the keys are the population
        names and the values the best individuals for those populations.

        :return: A dictionary with the best individual of each population.
        """
        return {p.name: p[0] for p in self.populations}


class SimpleGA(GeneticAlgorithm):
    """ Simple implementation of a GeneticAlgorithm

    This subclass abstracts all the behavior of the evolution over several
    populations.
    """

    def __init__(
        self,
        stop_condition,
        size,
        replacement_rate,
        spawning_pool,
        fitness,
        selection,
        replacement,
        recombination,
        p_recombination=1.0,
        mutation=NoMutation(),
        p_mutation=0.0,
    ):
        """ Initializes this instance.

        :param stop_condition: The condition to be met in order to stop the
            genetic algorithm.
        :param size: The size this population should have.
        :param replacement_rate: The rate of individuals to be replaced in each
            step of the algorithm. Must be a float value in the (0, 1] interval.
        :param spawning_pool: The object that generates individuals.
        :param fitness: The method to evaluate individuals.
        :param selection: The method to select individuals of the population to
            recombine.
        :param replacement: The method that will add and remove individuals from
            the population given the set of old individuals (i.e. the ones on
            the population before the evolution step) and new individuals (i.e.
            the offspring).
        :param recombination: The method to recombine parents in order to
            generate an offspring with characteristics of the parents. If none,
            no recombination will be applied.
        :param p_recombination: The odds for recombination method to be
            performed over a set of selected individuals to generate progeny. If
            not performed, progeny will be the parents. Must be a value between
            0 and 1 (both included). If not provided, defaults to 1.0.
        :param mutation: The method to mutate an individual. If none, no
            mutation over the individual will be applied. If not provided, no
            mutation is performed.
        :param p_mutation: The odds for mutation method to be performed over a
            progeny. It's applied once for each individual. If not performed the
            individuals will not be modified. Must be a value between 0 and 1
            (both included). If not provided, it defaults to 0.0 (no mutation is
            performed).
        :raises WrongValueForIntervalError: If any of the bounded values fall
            out of their respective intervals.
        :raises NotAProbabilityError: If a value was expected to be a
            probability and it wasn't.
        :raises UnexpectedClassError: If any of the input variables doesn't
            follow the contract required (i.e. doesn't inherit from a predefined
            class).
        """
        self.__population_name = 'SimpleGA'
        super().__init__(
            stop_condition=stop_condition,
            populations=[
                Population(
                    name=self.__population_name,
                    size=size,
                    replacement_rate=replacement_rate,
                    spawning_pool=spawning_pool,
                    fitness=fitness,
                    selection=selection,
                    recombination=recombination,
                    mutation=mutation,
                    replacement=replacement,
                    p_recombination=p_recombination,
                    p_mutation=p_mutation,
                )
            ],
            catastrophe=NoCatastrophe(),
        )

    def best(self):
        """ Returns the best individual obtained until now. """
        return super().best()[self.__population_name]
