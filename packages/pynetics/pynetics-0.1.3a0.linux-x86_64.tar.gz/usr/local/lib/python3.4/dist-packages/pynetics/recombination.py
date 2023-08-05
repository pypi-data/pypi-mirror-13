import abc

from .individuals import Individual


class Recombination(metaclass=abc.ABCMeta):
    """ Defines the behaviour of a recombination operator.

    A recombination operator takes a set of individuals (i.e. parents) and
    generates a different set of individuals (i.e. offspring) normally with
    aspects derived from their parents.
    """

    def __call__(self, *args):
        """ Applies the recombine method to a sequence of individuals.

        :param args: A list of one or more Individual instances to use as
            parents in the recombination.
        :returns: A sequence of individuals with characteristics of the parents.
        """
        if not args:
            msg = 'At least one individual is required for recombination'
            raise ValueError(msg)
        elif not all([isinstance(i, Individual) for i in args]):
            msg = 'All parameters should be Individual instances'
            raise ValueError(msg)
        else:
            return self.perform(*args)

    @abc.abstractmethod
    def perform(self, *args):
        """ Implementation of the recombine method.

        The method will always receive a list of Individual instances, and the
        implementation must be aware of the individual types because given that
        not all implementations are the same, not all the crossover operations
        may work.

        :param args: A list of one or more Individual instances to use as
            parents in the recombination.
        :returns: A sequence of individuals with characteristics of the parents.
        """


class NoRecombination(Recombination):
    """ A crossover method where no method is applied to the individuals. """

    def perform(self, *args):
        """ Return the same individuals passed as parameter. """
        return args
