from unittest import TestCase

from pynetics import Individual, UnexpectedClassError

from pynetics.ga_list import ListIndividual, SwapGenes, RandomGeneValue, \
    FiniteSetAlleles


class DummyNoListIndividual(Individual):
    """ An individual that is not a subclass of ListIndividual. """

    def phenotype(self):
        return None


class SwapGenesTestCase(TestCase):
    """ Tests for the SwapGenes mutate method. """

    def setUp(self):
        """ Common variables across the tests. """
        self.mutate = SwapGenes()

    def test_no_list_chromosome_raises_error(self):
        """ An error is raised when individuals is not a ListIndividual. """
        individual = DummyNoListIndividual()
        with self.assertRaises(UnexpectedClassError):
            self.mutate(individual)

    def test_check_genes_are_swapped(self):
        """ Checks that the genes of the individual are swapped.

        For this purpose, two checks are performed. First, the method checks if
        there are the same genes in the mutated individual. Second, it checks
        that only two genes has been moved from their positions.
        """
        genes = '0123456789'
        individual = ListIndividual()
        individual.extend(genes)
        self.mutate(individual)
        # Are all the genes in the individual?
        [self.assertIn(i, individual) for i in genes]
        # Are only two misplaced genes?
        different_genes = [i for i, j in zip(genes, individual) if i != j]
        self.assertEquals(len(different_genes), 2)


class RandomGeneValueTestCase(TestCase):
    """ Tests for the RandomGene mutate method. """

    def test_construction_is_correct(self):
        alleles = FiniteSetAlleles('ACTG')
        mutate = RandomGeneValue(alleles)

        self.assertEquals(mutate.alleles, alleles)

    def test_no_alleles_subclass_raises_error(self):
        """ An error is raised when initializing mutate method with other than
        an Alleles instance. """
        with self.assertRaises(UnexpectedClassError):
            RandomGeneValue(ListIndividual())

    def test_no_list_chromosome_raises_error(self):
        """ An error is raised when individuals is not a ListIndividual. """
        mutate = RandomGeneValue(FiniteSetAlleles('ACTG'))
        individual = DummyNoListIndividual()
        with self.assertRaises(UnexpectedClassError):
            mutate(individual)

    def test_check_genes_are_modified(self):
        """ Checks that the genes of the individual are modified.

        For this purpose, two checks are performed. First, the method checks if
        all except one gene are the same. Second, it checks that the different
        gene belongs to the list of allowed values.
        """
        alleles = 'ACTG'
        mutate = RandomGeneValue(FiniteSetAlleles('ACTG'))
        individual = ListIndividual()
        genes = 'ACTGACTGACTGACTG'
        individual.extend(genes)

        mutate(individual)
        # Have all the genes values allowed by the alleles?
        self.assertEquals([], [i for i in individual if i not in alleles])
        # Are all the genes (minus one) in the individual in the same position?
        different_genes = [i for i, j in zip(genes, individual) if i != j]
        self.assertEquals(len(different_genes), 1)
