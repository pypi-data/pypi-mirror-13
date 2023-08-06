import abc
import random
import collections

from pynetics.individuals import SpawningPool, Individual
from pynetics.recombination import Recombination
from pynetics.mutation import Mutation
from pynetics.utils import take_chances, check_is_instance_of


class Alleles(metaclass=abc.ABCMeta):
    """ The alleles are all the possible values a gene can take. """

    @abc.abstractmethod
    def get(self):
        """ Returns a random value of all the possible existent values. """


class FiniteSetAlleles(Alleles):
    """ The possible alleles belong to a finite set of symbols. """

    def __init__(self, values):
        """ Initializes this set of alleles with its sequence of symbols.

        The duplicated values are removed in the list maintained by this alleles
        class, but the order is maintained.

        :param values: The sequence of symbols.
        """
        # TODO Tiene toda la pinta de que se pueda mantener como Sequence
        values = check_is_instance_of(values, collections.Sequence)
        self.__values = list(collections.OrderedDict.fromkeys(values))

    def get(self):
        """ A random value is selected uniformly over the set of values. """
        return random.choice(self.__values)

    @property
    def values(self):
        """ Returns the list of values for genes allowed by this instance. """
        return self.__values[:]


class ListIndividualSpawningPool(SpawningPool, metaclass=abc.ABCMeta):
    """ Defines the methods for creating individuals required by population. """

    def __init__(self, size, alleles):
        """ Initializes this spawning pool for generating list individuals.

        :param size: The size of the individuals to be created from this
            spawning pool.
        :param alleles: The alleles to be used as values of the genes.
        """
        self.size = size
        self.alleles = alleles

    def create(self):
        """ Creates a new individual randomly.

        :return: A new Individual object.
        """
        individual = ListIndividual()
        for _ in range(self.size):
            individual.append(self.alleles.get())
        return individual


class ListIndividual(Individual, list):
    """ An individual whose representation is a list of finite values. """

    def __eq__(self, individual):
        """ The equality between two list individuals is True if they:

        1. Have the same length
        2. Any two genes in the same position have the same value.
        """
        return len(self) == len(individual) and all(
                [x == y for (x, y) in zip(self, individual)]
        )

    def phenotype(self):
        return self[:]


class ListRecombination(Recombination, metaclass=abc.ABCMeta):
    """ Common behavior for crossover methods over ListIndividual instances. """

    def __call__(self, *args):
        """ Performs some checks before applying the crossover method.

        Specifically, it checks if the length of all individuals are the same.
        In so, the crossover operation is done. If not, a ValueError is raised.

        :param args: The individuals to cross to generate progeny.
        :return: A list of individuals with characteristics of the parents.
        :raises ValueError: If not all the individuals has the same length.
        """
        lengths = [len(i) for i in args]
        if not lengths.count(lengths[0]) == len(lengths):
            raise ValueError('Both individuals must have the same length')
        else:
            return super().__call__(*args)


class OnePointRecombination(ListRecombination):
    """ Offspring is created by mixing the parents using one random pivot point.

    This crossover implementation works with two (and only two) individuals of
    type ListIndividual (or subclasses).
    """

    def __call__(self, parent1, parent2):
        """ Performs some checks before applying the crossover method.

        Specifically, the constructor forces the number of parameters to 2.

        :param parent1: One of the individuals from which generate the progeny.
        :param parent2: The other.
        :return: A list of individuals with characteristics of the parents.
        :raises ValueError: If not all the individuals has the same length.
        """
        return super().__call__(parent1, parent2)

    def perform(self, parent1, parent2):
        """ Offspring is obtained mixing the parents with one pivot point.

        One example:

        parents  : aaaaaaaa, bbbbbbbb
        pivot    : 3
        -----------
        children : aaabbbbb, bbbaaaaa

        :param parent1: One of the individuals from which generate the progeny.
        :param parent2: The other.
        :return: A list of two individuals, each a child containing some
            characteristics from their parents.
        """
        child1, child2 = parent1.population.spawn(), parent1.population.spawn()

        p = random.randint(1, len(parent1) - 1)
        for i in range(len(parent1)):
            if i < p:
                child1[i], child2[i] = parent1[i], parent2[i]
            else:
                child1[i], child2[i] = parent2[i], parent1[i]
        return [child1, child2, ]


class TwoPointRecombination(ListRecombination):
    """ Offspring is created by mixing the parents using two random pivot point.

    This crossover implementation works with two (and only two) individuals of
    type ListIndividual (or subclasses).
    """

    def __call__(self, parent1, parent2):
        """ Performs some checks before applying the crossover method.

        Specifically, the constructor forces the number of parameters to 2.

        :param parent1: One of the individuals from which generate the progeny.
        :param parent2: The other.
        :return: A list of individuals with characteristics of the parents.
        :raises ValueError: If not all the individuals has the same length.
        """
        return super().__call__(parent1, parent2)

    def perform(self, parent1, parent2):
        """ Offspring is obtained mixing the parents with two pivot point.

        One example:

        parents  : aaaaaaaa, bbbbbbbb
        pivot    : 3, 5
        -----------
        children : aaabbaaa, bbbaabbb

        :param parent1: One of the individuals from which generate the progeny.
        :param parent2: The other.
        :return: A list of two individuals, each a child containing some
            characteristics from their parents.
        """
        child1, child2 = parent1.population.spawn(), parent2.population.spawn()

        pivots = random.sample(range(len(parent1) - 1), 2)
        p, q = min(pivots[0], pivots[1]), max(pivots[0], pivots[1])
        for i in range(len(parent1)):
            if p < i < q:
                child1[i], child2[i] = parent1[i], parent2[i]
            else:
                child1[i], child2[i] = parent2[i], parent1[i]
        return [child1, child2, ]


class RandomMaskRecombination(ListRecombination):
    """ Offspring is created by using a random mask.

    This crossover implementation works with two (and only two) individuals of
    type ListIndividual (or subclasses).
    """

    def perform(self, individuals):
        """ Offspring is obtained generating a random mask.

        This mask determines which genes of each of the progenitors are used on
        each of the the genes. For example:

        parents     : aaaaaaaa, bbbbbbbb
        random mask : 00100110
        -----------
        children    : aabaabba, bbabbaab

        :param individuals: The individuals to cross to generate progeny.
        :return: A list of two individuals, each a child containing some
            characteristics from their parents.
        """
        i1, i2 = individuals[0], individuals[1]
        child1, child2 = i1.population.spawn(), i1.population.spawn()

        for i in range(len(i1)):
            if take_chances(.5):
                child1[i], child2[i] = i1[i], i2[i]
            else:
                child1[i], child2[i] = i2[i], i1[i]
        return [child1, child2, ]


class ListMutation(Mutation, metaclass=abc.ABCMeta):
    """ Common behavior for mutation methods over ListIndividual instances. """

    def __call__(self, individual):
        """ Performs some checks before applying the mutate method.

        Specifically, it checks if the individual is a ListIndividual or any of
        its subclasses. If not, a ValueError is raised.

        :param individual: The individual to be mutated.
        :raises UnexpectedClassError: If the individual is not a subclass of the
            class ListIndividual.
        """
        return super().__call__(check_is_instance_of(
                individual,
                ListIndividual
        ))


class SwapGenes(ListMutation):
    """ Mutates the by swapping two random genes.

    This mutation method operates only with ListIndividuals (or any of their
    subclasses.
    """

    def perform(self, individual):
        """ Swaps the values of two positions of the list of values.

        When the individual is mutated, two random positions (pivots) are
        generated. Then, the values of those positions are swapped. For example:

        individual : 12345678
        pivot      : 3, 5
        -----------
        mutated    : 12365478

        :param individual: The individual to be mutated.
        """
        genes = random.sample(range(len(individual) - 1), 2)
        g1, g2 = genes[0], genes[1]
        individual[g1], individual[g2] = individual[g2], individual[g1]


class RandomGeneValue(ListMutation):
    """ Mutates the individual by changing the value to a random gene. """

    def __init__(self, alleles):
        """ Initializes the mutation method.

        :param alleles: The alleles that the genes of the individual can take.
        """
        self.__alleles = check_is_instance_of(alleles, Alleles)

    @property
    def alleles(self):
        """ Returns the alleles that uses this mutation method. """
        return self.__alleles

    def perform(self, individual):
        """ Changes the value of a random gene of the individual.

        The mutated chromosome is obtained by changing a random gene as seen in
        the next example:

        individual : aabbaaba
        alleles    : (a, b, c, d)
        change pos : 7
        -----------
        mutated    : aabdaabc

        :param individual: The individual to be mutated.
        """
        i = random.choice(range(len(individual)))
        new_gene = self.alleles.get()
        while individual[i] == new_gene:
            new_gene = self.alleles.get()
        individual[i] = new_gene
        return individual
