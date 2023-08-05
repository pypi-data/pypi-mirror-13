from unittest import TestCase

from pynetics import GeneticAlgorithm, Fitness, SpawningPool, Population
from pynetics.catastrophe import NoCatastrophe
from pynetics.recombination import NoRecombination
from pynetics.ga_list import ListIndividual
from pynetics.mutation import NoMutation
from pynetics.replacements import LowElitism
from pynetics.selections import BestIndividual
from pynetics.stop import StepsNumStopCondition


class DummySpawningPool(SpawningPool):
    """ A spawning pool just for tests. """

    def create(self):
        """ Return one of the individuals in the list, consecutively. """
        l = ListIndividual()
        l.extend('1234567890')
        return l


class DummyFitness(Fitness):
    def perform(self, individual):
        return 1


class TestGeneticAlgorithm(TestCase):
    def test_generations_pass(self):
        """ Generation increment works properly. """
        steps = 10
        ga = GeneticAlgorithm(
            StepsNumStopCondition(steps),
            [
                Population(100, 50, DummySpawningPool(), DummyFitness())
            ],
            BestIndividual(),
            LowElitism(),
            NoRecombination(2),
            NoMutation(),
            NoCatastrophe(),
            0.75,
            0.1,
        )
        ga.run()
        self.assertEquals(ga.generation, steps)
