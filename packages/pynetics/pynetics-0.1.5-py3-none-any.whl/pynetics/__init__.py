import inspect
import math

import abc
import random

from pynetics.catastrophe import Catastrophe
from pynetics.exceptions import WrongValueForInterval, NotAProbabilityError
from pynetics.individuals import SpawningPool, Individual
from pynetics.mutation import Mutation, NoMutation
from pynetics.recombination import Recombination, NoRecombination
from pynetics.replacements import Replacement
from pynetics.selections import Selection
from pynetics.stop import StopCondition
from pynetics.utils import check_is_instance_of, take_chances

__version__ = '0.1.5'


class Population(list):
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
        fitness=None,
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
        :param fitness: The method to evaluate individuals.
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
        super().__init__()

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
        self.fitness = check_is_instance_of(fitness, Fitness)
        self.selection = check_is_instance_of(selection, Selection)
        self.recombination = check_is_instance_of(recombination, Recombination)
        self.p_recombination = p_recombination
        self.mutation = check_is_instance_of(mutation, Mutation)
        self.p_mutation = p_mutation
        self.replacement = check_is_instance_of(replacement, Replacement)

        self.sorted = False
        self.genetic_algorithm = None

        # Precomputed values to speed up the things a bit
        self.offspring_size = int(math.ceil(size * replacement_rate))
        self.selection_size = len(
            inspect.signature(recombination.perform).parameters
        )

        # Population is initialized with the individuals, and they are sorted by
        # their initial fitness computation (method init_perform)
        individuals = individuals or []
        self.extend(random.sample(
            individuals,
            min(self.size, len(individuals)))
        )
        [self.append(self.spawn()) for _ in range(len(individuals), self.size)]
        self.sort(key=lambda i: self.fitness(i, init=True))

    def spawn(self):
        """ Spawns a new individual.

        This individual will have a reference to the population which created
        it, but the population itself will not have the individual included in
        it until "append" method is called.

        :return: An individual of the class of the individuals created by the
            spawning pool defined in the initialization.
        """
        individual = self.spawning_pool.create()
        individual.population = self
        return individual

    def sort(self, *args, **kwargs):
        """ Sorts the list of individuals by its fitness.

        The key may be overridden, but is not recommended. It's overridden at
        initialization time when performing the initial ordering, using
        init_perform instead perform.

        :param args: Positional parameters (inherited from list class).
        :param kwargs: Named parameters (inherited from list class).
        """
        if not self.sorted:
            super().sort(
                key=kwargs.get('key', self.fitness),
                reverse=True
            )
            self.sorted = True

    def __getitem__(self, index):
        """ Returns the individual located on this position.

        Treat this call as if population were sorted by fitness, from the
        fittest to the less fit.

        :param index: The index of the individual to recover.
        :return: The individual.
        """
        self.sort()
        return super().__getitem__(index)

    def __setitem__(self, index, individual):
        """ Puts the named individual in the specified position.

        This call will cause a new sorting of the individuals the next time an
        access is required. This means that is preferable to make all the
        inserts in the population at once instead doing interleaved readings and
        inserts.

        :param index: The position where to insert the individual.
        :param individual: The individual to be inserted.
        """
        self.sorted = False
        self.__setitem__(index, individual)
        individual.population = self

    def extend(self, individuals):
        """ Extends the population with a collection of individuals.

        This call will cause a new sorting of the individuals the next time an
        access is required. This means that is preferable to make all the
        inserts in the population at once instead doing interleaved readings and
        inserts.

        :param individuals: A collection of individuals to be inserted into the
            population.
        """
        self.sorted = False
        for individual in individuals:
            individual.population = self
        super().extend(individuals)

    def append(self, individual):
        """ Ads a new element to the end of the list of the population.

        This call will cause a new sorting of the individuals the next time an
        access is required. This means that is preferable to make all the
        inserts in the population at once instead doing interleaved readings and
        inserts.

        :param individual: The individual to be inserted in the population
        """
        self.sorted = False
        individual.population = self
        super().append(individual)

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


class Fitness(metaclass=abc.ABCMeta):
    """ Method to estimate how adapted is the individual to the environment. """

    def __call__(self, individual, init=False):
        """ Calculates the fitness of the individual.

        This method does some checks and the delegates the computation of the
        fitness to the "perform" method.

        :param individual: The individual to which estimate the adaptation.
        :param init: If this call to fitness is at initialization time. It
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
