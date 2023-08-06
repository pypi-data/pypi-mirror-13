import unittest

from pynetics.individuals import Individual


class IndividualTestCase(unittest.TestCase):
    """ Tests for Individual instances. """

    def test_no_population_is_related_to_individual(self):
        """ An individual is created with no reference to any population. """
        self.assertIsNone(Individual().population)
