import abc

from pynetics.utils import check_is_instance_of
from pynetics.individuals import Individual


class Mutation(metaclass=abc.ABCMeta):
    """ Defines the behaviour of a genetic algorithm mutation operator. """

    def __call__(self, individual):
        """ Applies the crossover method to the list of individuals.

        :param individual: an individual to mutate.
        :returns: A new mutated individual.
        :raises UnexpectedClassError: If the individual is not an Individual
            instance.
        """
        individual = check_is_instance_of(individual, Individual)
        return self.perform(individual)

    @abc.abstractmethod
    def perform(self, individual):
        """ Implementation of the mutation operation.

        The mutation implementation must be aware of the implementation type.
        Given that not all the implementations are the same, not all the
        mutation operations may work.

        :param individual: The individual to mutate.
        :returns: A new mutated individual.
        """


class NoMutation(Mutation):
    """ A method where no modification is performed to the individual. """

    def perform(self, individual):
        """ Return the same individual passed as parameter.

        :param individual: The individual to mutate.
        :returns: The same, unmodified individual.
        """
        return individual
