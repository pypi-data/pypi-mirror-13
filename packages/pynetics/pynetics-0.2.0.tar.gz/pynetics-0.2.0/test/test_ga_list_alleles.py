from unittest import TestCase

from pynetics import UnexpectedClassError
from pynetics.ga_list import FiniteSetAlleles


class FiniteSetAllelesTestCase(TestCase):
    """ All the tests for the FiniteSetAlleles class. """

    def test_construction_with_a_non_sequence_values_raises_error(self):
        """ Construction raises error if initialized with a non sequence. """
        for no_sequence in [{}, 123, set()]:
            with self.assertRaises(UnexpectedClassError):
                FiniteSetAlleles(no_sequence)

    def test_alleles_maintains_a_list_of_no_duplicated_values(self):
        """ The values in the maintained without duplicated values. """
        values = 'ACTGACTGTGCA'
        alleles = FiniteSetAlleles(values)

        # Are there any duplicated values?
        self.assertEquals(len(alleles.values), len(set(alleles.values)))
        # Are the values in the alleles contained in the initialization list?
        [self.assertIn(a, alleles.values) for a in values]
        # Are the values in the initialization list contained in the alleles?
        [self.assertIn(a, values) for a in alleles.values]
