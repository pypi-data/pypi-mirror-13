import copy
import unittest

from pynetics import NoMutation
from pynetics.exceptions import UnexpectedClassError
from pynetics.individuals import Individual


class NoRecombinationTestCase(unittest.TestCase):
    """ Tests for NoMutation instances. """

    def test_call_with_none(self):
        """ A value of None is not an Individual instance. """
        mutation = NoMutation()
        with self.assertRaises(UnexpectedClassError):
            mutation(None)

    def test_call_with_no_individual_instance(self):
        """ A non Individual instance for argument leads to an error. """
        mutation = NoMutation()
        with self.assertRaises(UnexpectedClassError):
            mutation('A very interesting individual')

    def test_call_with_valid_individual_remains_individual_untouched(self):
        """ A valid individual in a NoMutation method remains untouched. """
        individual = Individual()
        mutation = NoMutation()
        mutated_individual = mutation(individual)
        self.assertEqual(individual, mutated_individual)
