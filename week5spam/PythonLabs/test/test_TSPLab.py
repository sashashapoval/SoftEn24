import unittest

from PythonLabs.TSPLab import *

class TSPTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nTSPLab:  ", end = "")
        
    def setUp(self):
        self.m = Map(path_to_data("test7.txt"))
        
    # Test the factorial method

    def test_01_fact(self):
        self.assertEqual(120, factorial(5), '5! should be 120')
        self.assertEqual(1, factorial(1), '1! shoule be 0')
        self.assertEqual(1, factorial(0), '0! shoule be 0')
        
    # ntours(n) should compute (n-1)! / 2

    def test_02_ntours(self):
        n = 10
        self.assertEqual(362880, factorial(n-1), '9! should be 362880')
        self.assertEqual(181440, ntours(n), 'wrong number of tours for n = 10')

    # Our implementation of 'permutations' works on strings and sequences
    
    def test_03_each_permutation(self):
        a = [x for x in each_permutation("ABC")]
        self.assertEqual(6, len(a), 'should be 6 permutations of 3 items')
        self.assertEqual(["ABC", "ACB", "BAC", "BCA", "CAB", "CBA"], a, 'permutations returned wrong strings')
        a = [x for x in each_permutation([3,2,1])]
        self.assertEqual([(3, 2, 1), (3, 1, 2), (2, 3, 1), (2, 1, 3), (1, 3, 2), (1, 2, 3)], a, 'permutations returned wrong tuples')
      
    # Check internal properties of the test map
    
    def test_04_make_map(self):
        self.assertEqual(['A', 'B', 'C', 'D', 'E', 'F', 'G'], self.m._labels)
        i = self.m._index_of('A')
        self.assertEqual((192, 212), self.m._coords[i])
        j = self.m._index_of('G')
        self.assertEqual((433, 133), self.m._coords[j])

    # Test Map accessor methods using the test map
    
    def test_05_map(self):
        self.assertEqual(7, self.m.size())
        self.assertEqual(['A', 'B', 'C', 'D', 'E', 'F', 'G'], self.m.cities())
        self.assertEqual((192, 212), self.m.coords('A'))
        self.assertEqual((433, 133), self.m.coords('G'))
        self.assertAlmostEqual(151.54, self.m['A', 'B'])
        self.assertAlmostEqual(151.54, self.m['B', 'A'])
        self.assertAlmostEqual(144.51, self.m['F', 'G'])
        self.assertIsNone(self.m['A', 'x'])
        self.assertIsNone(self.m['x', 'A'])
  
    # Make, examine tours with known paths

    def test_06_make_tour(self):
        t = self.m.make_tour()
        self.assertEqual(('A', 'B', 'C', 'D', 'E', 'F', 'G'), t.path())
        t = self.m.make_tour(['A', 'B', 'C'])
        self.assertEqual(('A', 'B', 'C'), t.path())
        self.assertAlmostEqual((self.m['A','B'] + self.m['B','C'] + self.m['C','A']), t.cost())
        self.assertEqual(2, Tour.count())
        
    # Exhaustive search for best tour -- record the best tour, and check to
    # to make sure each tour was generated (by checking the count of the number made)

    def test_07_exhaustive(self):
        best = self.m.make_tour('random')
        Tour.reset()
        for t in self.m.each_tour():
            if t.cost() < best.cost():
                best = t
        self.assertAlmostEqual(1185.43, best.cost())
        self.assertEqual(ntours(self.m.size()), Tour.count())

    # Point mutation test with a switch in the middle of the tour.  As an optimization
    # the mutate method doesn't call pathcost() to sum over the entire path; this test
    # uses pathcost() to verify the optimized version is correct.

    def test_08_mutate_middle(self):
        t = self.m.make_tour([ 'A', 'B', 'C', 'D', 'E', 'F', 'G' ])
        tc = t.cost()
        t.mutate(i = 2)
        self.assertEqual(('A', 'B', 'D', 'C', 'E', 'F', 'G'), t.path())
        self.assertAlmostEqual(t.cost(), t.pathcost())
        t.mutate(i = 2)
        self.assertEqual(('A', 'B', 'C', 'D', 'E', 'F', 'G'), t.path())
        self.assertAlmostEqual(t.cost(), tc)

    # Same as the previous test, making sure a mutation at the end wraps around.

    def test_09_mutate_wrap(self):
        t = self.m.make_tour([ 'A', 'B', 'C', 'D', 'E', 'F', 'G' ])
        tc = t.cost()
        t.mutate(i = 6)
        self.assertEqual(('G', 'B', 'C', 'D', 'E', 'F', 'A'), t.path())
        self.assertAlmostEqual(t.cost(), t.pathcost())
        t.mutate(i = 6)
        self.assertEqual(('A', 'B', 'C', 'D', 'E', 'F', 'G'), t.path())
        self.assertAlmostEqual(t.cost(), tc)
        t.mutate(i = 0)
        self.assertEqual(('B', 'A', 'C', 'D', 'E', 'F', 'G'), t.path())
        self.assertAlmostEqual(t.cost(), t.pathcost())
        t.mutate(i = 0)
        t.mutate(i = 5)
        self.assertEqual(('A', 'B', 'C', 'D', 'E', 'G', 'F'), t.path())
        t.mutate(i = 5)
        self.assertAlmostEqual(t.cost(), t.pathcost())
        self.assertAlmostEqual(t.cost(), tc)

    # Point mutation test -- d  > 1, both in the middle and at the ends

    def test_10_mutate_delta(self):
        m = Map(10)
        t = m.make_tour()
        tc = t.cost()

        t.mutate(i = 2, distance = 4)
        self.assertEqual((0,1,6,3,4,5,2,7,8,9), t.path())
        self.assertAlmostEqual(t.cost(), t.pathcost())
        t.mutate(i = 2, distance = 4)

        t.mutate(i = 2, distance = 7)
        self.assertEqual((0,1,9,3,4,5,6,7,8,2), t.path())
        self.assertAlmostEqual(t.cost(), t.pathcost())
        t.mutate(i = 2, distance = 7)

        t.mutate(i = 2, distance = 8)
        self.assertEqual((2,1,0,3,4,5,6,7,8,9), t.path())
        self.assertAlmostEqual(t.cost(), t.pathcost())
        t.mutate(i = 2, distance = 8)

        self.assertAlmostEqual(t.cost(), tc)
        
    # Test cross-over mutations; method calls pathcost() so no need to test
    # cost.  Test cases include intact subtour and wraparound subtour.

    def test_11_cross(self):
        m = Map(10)
        tfwd = m.make_tour([0,1,2,3,4,5,6,7,8,9])
        trev = m.make_tour([9,8,7,6,5,4,3,2,1,0])
        
        t = tfwd.clone()
        t.cross(trev, i = 3, size = 4)
        self.assertEqual((3,4,5,6,9,8,7,2,1,0), t.path())

        t = tfwd.clone()
        t.cross(trev, i = 8, size = 4)
        self.assertEqual((8,9,0,1,7,6,5,4,3,2), t.path())
        
    # Test the 'mutate' and 'cross' options for make_tour.  New tours are copies
    # of existing tours with mutations added.
    
    def test_12_make_tour(self):
        m = Map(10)
        tfwd = m.make_tour([0,1,2,3,4,5,6,7,8,9])
        trev = m.make_tour([9,8,7,6,5,4,3,2,1,0])
        
        t = m.make_tour('mutate', tfwd, i = 4, distance =  1)
        self.assertEqual((0,1,2,3,5,4,6,7,8,9), t.path())
        t = m.make_tour('mutate', tfwd, i = 4, distance =  3)
        self.assertEqual((0,1,2,3,7,5,6,4,8,9), t.path())
        
        t = m.make_tour('cross', tfwd, trev, i = 3, size = 4)
        self.assertEqual((3,4,5,6,9,8,7,2,1,0), t.path())
        t = m.make_tour('cross', tfwd, trev, i = 8, size = 4)
        self.assertEqual((8,9,0,1,7,6,5,4,3,2), t.path())
        
        t = m.make_tour('mutate', tfwd)
        self.assertEqual(sorted(tfwd.path()), sorted(t.path()))

        t = m.make_tour('cross', tfwd, trev)
        self.assertEqual(sorted(tfwd.path()), sorted(t.path()))

    # Test the random search algorithm.  Not much can be done -- just count the
    # number of tours created?  
    
    def test_13_rsearch(self):
        t = rsearch(self.m, 100)
        self.assertEqual(100, Tour.count())

        