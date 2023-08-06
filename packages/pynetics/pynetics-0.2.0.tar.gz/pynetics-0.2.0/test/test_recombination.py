import unittest

from pynetics import NoRecombination
from pynetics.individuals import Individual


class NoRecombinationTestCase(unittest.TestCase):
    """ Tests for NoRecombination instances. """

    def test_call_without_any_argument(self):
        """ A recombination without arguments raises an error. """
        recombination = NoRecombination()
        with self.assertRaises(ValueError):
            recombination()

    def test_call_with_one_non_individual_in_arguments(self):
        """ All arguments for recombination must be Individual instances.

        This test will run the recombination with only one non Individual
        argument.
        """
        individuals = [Individual(), Individual(), 'HappyIndividual']
        recombination = NoRecombination()
        with self.assertRaises(ValueError):
            recombination(*individuals)

    def test_call_with_some_non_individuals_in_arguments(self):
        """ All arguments for recombination must be Individual instances.

        This test will run the recombination with all but one non Individual
        arguments.
        """
        individuals = [Individual(), 'HappyIndividual', 'HappyIndividual']
        recombination = NoRecombination()
        with self.assertRaises(ValueError):
            recombination(*individuals)

    def test_call_with_all_non_individual_in_arguments(self):
        """ All arguments for recombination must be Individual instances.

        This test will run the recombination with all non Individual arguments.
        """
        individuals = ['HappyIndividual', 'HappyIndividual', 'HappyIndividual']
        recombination = NoRecombination()
        with self.assertRaises(ValueError):
            recombination(*individuals)

    def test_call_with_correct_arguments(self):
        """ All arguments are Individual instances.

        The tests only checks that no error is raised if no individual is wrong.
        """
        individuals = [Individual(), Individual(), Individual()]
        recombination = NoRecombination()
        recombination(*individuals)

    def test_perform_does_not_mess_with_arguments(self):
        """ The parents and the generated progeny must be the same. """
        individuals = [Individual(), Individual(), Individual(), Individual()]
        progeny = NoRecombination().__call__(*individuals)
        self.assertSequenceEqual(individuals, progeny)
