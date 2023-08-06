import unittest

from pynetics import Population, SpawningPool, Individual, Fitness, \
    NoRecombination, NoMutation
from pynetics.replacements import LowElitism, Replacement
from pynetics.selections import BestIndividual


class PopulationLengthModReplacement(Replacement):
    """ Dummy replacement that modifies population length. """

    def perform(self, population, offspring):
        """ Removes the last individual. """
        del population[-1]


class NoReplacement(Replacement):
    """ Dummy replacement that does not modifies population length. """

    def perform(self, population, offspring):
        """ Maintains the population as is.      """
        pass


class DummySpawningPool(SpawningPool):
    def create(self):
        return Individual()


class DummyFitness(Fitness):
    def perform(self, individual):
        return id(individual)


class DummyPopulation(Population):
    """ A population with defaults to test replacement methods behavior. """
    def __init__(self):
        super().__init__(
            name='test_population',
            size=10,
            replacement_rate=.5,
            p_recombination=1,
            p_mutation=0,
            spawning_pool=DummySpawningPool(),
            fitness=DummyFitness(),
            selection=BestIndividual(),
            recombination=NoRecombination(),
            mutation=NoMutation(),
            replacement=NoReplacement(),
        )


class ReplacementTestCase(unittest.TestCase):
    """ Tests for base behavior of replacement methods. """

    def test_error_is_raised_when_maintaining_population_size(self):
        """ Error when retain size set and population is modified. """
        replacement = PopulationLengthModReplacement()
        population = DummyPopulation()
        offspring = population[:]
        with self.assertRaises(ValueError):
            replacement(population, offspring)

    def test_no_error_is_raised_when_maintaining_population_size(self):
        """ No error when retain size set and population is not modified. """
        replacement = NoReplacement()
        population = DummyPopulation()
        offspring = population[:]
        replacement(population, offspring)

    def test_no_error_is_raised_when_no_maintaining_population_size(self):
        """ No error when retain size is False and population is modified. """
        replacement = PopulationLengthModReplacement(
                maintain_population_size=False
        )
        population = DummyPopulation()
        offspring = population[:]
        replacement(population, offspring)


class LowElitismTestCase(unittest.TestCase):
    """ Tests for low elitism replacement method. """

    def test_maintain_population_size_defaults_to_true(self):
        """ When not specified, the parameter defaults to True. """
        replacement = LowElitism()
        self.assertTrue(replacement.maintain_population_size)

    def test_maintain_population_size(self):
        """ When specified, the parameter is maintained. """
        replacement = LowElitism(maintain_population_size=True)
        self.assertTrue(replacement.maintain_population_size)
        replacement = LowElitism(maintain_population_size=False)
        self.assertFalse(replacement.maintain_population_size)
    # TODO test the logic


class HighElitismTestCase(unittest.TestCase):
    """ Tests for low elitism replacement method. """

    def test_maintain_population_size_defaults_to_true(self):
        """ When not specified, the parameter defaults to True. """
        replacement = LowElitism()
        self.assertTrue(replacement.maintain_population_size)

    def test_maintain_population_size(self):
        """ When specified, the parameter is maintained. """
        replacement = LowElitism(maintain_population_size=True)
        self.assertTrue(replacement.maintain_population_size)
        replacement = LowElitism(maintain_population_size=False)
        self.assertFalse(replacement.maintain_population_size)
    # TODO test the logic
