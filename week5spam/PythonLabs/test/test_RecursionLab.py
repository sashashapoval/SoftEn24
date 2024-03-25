import unittest

from PythonLabs.RecursionLab import *

class RecursionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nRecursionLab:  ", end = "")

    def test_01_bsearch(self):
        "bsearch(a, x) uses a binary search to find item x in array a"
        a = ["Au", "C", "Cu", "H", "He", "O", "Pb"]
        self.assertEqual(0,bsearch(a, "Au"), "didn't find item at the front")
        self.assertEqual(2,bsearch(a, "Cu"), "didn't find item in the middle")
        self.assertEqual(6,bsearch(a, "Pb"), "didn't find item at the end")
        self.assertIsNone(bsearch(a, "Al"), "found something that wasn't there")
        self.assertIsNone(bsearch(a, "Co"), "found something that wasn't there")
        self.assertIsNone(bsearch(a, "P"), "found something that wasn't there")
        self.assertIsNone(bsearch(a, "Zn"), "found something that wasn't there")

    def test_03_msort(self):
        "Compare result of msort(a) with the built-in sort method"
        for n in [15,16,17]:
            a = RandomList(n)
            a2 = list(a)
            a2.sort()
            msort(a)
            self.assertEqual(a, a2, "sorted lists of length %d differ" % n)

    def test_04_qsort(self):
        "Compare result of qsort(a) with the built-in sort method"
        for n in [15,16,17]:
            a = RandomList(n)
            a2 = list(a)
            a2.sort()
            qsort(a)
            self.assertEqual(a, a2, "sorted lists of length %d differ" % n)
