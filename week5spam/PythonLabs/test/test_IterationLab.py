import unittest

from PythonLabs.IterationLab import *

class IterationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nIterationLab:  ", end = "")

    def test_01_search(self):
        "search(a, x) scans the list a to find item x"
        a = ["fee", "fie", "foe", "fum"]
        self.assertEqual(isearch(a, "fee"), 0, "didn't find item at the front")
        self.assertEqual(isearch(a, "fie"), 1, "didn't find item in the middle")
        self.assertEqual(isearch(a, "fum"), 3, "didn't find item at the end")
        self.assertIsNone(isearch(a, "foo"), "found something that wasn't there")

    def test_02_move_left(self):
        "move_left(a,i) is the helper function for isort"
        a = [1,2,4,5,3,8,0,7]
        move_left(a,4)
        self.assertEqual([1,2,3,4,5,8,0,7], a, "item not where it belongs")
        move_left(a,4)
        self.assertEqual([1,2,3,4,5,8,0,7], a, "item moved when it shouldn't")

    def test_03_isort(self):
        "Compare result of isort(a) with the built-in sort method"
        for n in [15,16,17]:
            a = RandomList(n)
            a2 = list(a)
            a2.sort()
            isort(a)
            self.assertEqual(a, a2, "sorted lists of length %d differ" % n)

    def test_04_counters(self):
        "Check counter values after calls to isearch and isort"
        a = RandomList(10)
        loc = isearch(a, a.random('success'))
        self.assertLessEqual(Counter.value('comparisons'), len(a), "too many comparisons by isearch")
        loc = isearch(a, a.random('fail'))
        self.assertEqual(Counter.value('comparisons'), len(a), "failed linear search should make len(a) comparisons")
        
        a = RandomList(10)
        isort(a)
        self.assertLess(Counter.value('comparisons'), len(a)**2 / 2, "too many comparisons by isort")
        isort(a)
        self.assertEqual(Counter.value('comparisons'), len(a)-1, "list already sorted, should be n-1 comparisons")

        