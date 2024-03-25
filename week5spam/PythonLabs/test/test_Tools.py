import unittest

from PythonLabs.Tools import *

class IterationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nTools:  ", end = "")
        
    # Test for the RandomList constructor -- make lists of integers and strings

    def test_01_ints(self):
        "RandomList(n) should create a list of n random integers"
        a = RandomList(5)
        self.assertEqual(5, len(a), "list doesn't have 5 items")
        for n in a:
            self.assertEqual(int, type(n), "item isn't an integer")

    def test_02_ints(self):
        "RandomList(n, m) should create a list of n random integers between 0 and m-1"
        a = RandomList(5, 10)
        self.assertEqual(5, len(a), "list doesn't have 5 items")
        for n in a:
            self.assertTrue(n < 10, "item outside expected range")
            self.assertTrue(n >= 0, "item outside expected range")

    def test_03_fish(self):
        "Make a list of random fish names, check each item against a list of all fish names"
        allfish = RandomList('all','fish')
        self.assertEqual(55, len(allfish))
        self.assertEqual('catfish', allfish[0], "expected 'catfish'")
        self.assertEqual('sardine', allfish[-1], "expected 'sardine'")
        rfish = RandomList(5, 'fish')
        for f in rfish:
            self.assertTrue(f in allfish, "item isn't a fish")
            
    # Test construction of sorted lists
    
    def test_04_sorted_ints(self):
        "Make a sorted list of ints"
        a = RandomList(10, sorted=True)
        self.assertEqual(10, len(a), "list doesn't have 10 items")
        for i in range(0,len(a)-1):
            self.assertLess(a[i], a[i+1], "list out of order")
        
    def test_05_sorted_int_range(self):
        "Make a sorted list of ints less than 1000"
        a = RandomList(10, 1000, sorted=True)
        self.assertEqual(10, len(a), "list doesn't have 10 items")
        m = a[-1]
        for i in range(0,len(a)-1):
            self.assertLess(a[i], a[i+1], "list out of order")
            if a[i] > m: m = a[i]
        self.assertLess(m, 1000, "max greater than 1000")
        
    def test_06_sorted_fish(self):
        "Make a sorted list of fish"
        allfish = RandomList('all','fish')
        a = RandomList(10, 'fish', sorted=True)
        self.assertEqual(10, len(a), "list doesn't have 10 items")
        for i in range(0,len(a)-1):
            self.assertLess(a[i], a[i+1], "list out of order")
            self.assertTrue(a[i] in allfish, "item isn't a fish")
        
    # Test illegal combinations of arguments passed to the RandomList constructor

    def test_07_ints(self):
        "Upper bound should be at least twice the list size"
        with self.assertRaises(RandomSourceError) as context:
            a = RandomList(5,5)
        self.assertEqual(type(context.exception), RandomSourceError, "wrong exception type")

    def test_08_infinite(self):
        "Can't make a list with all integers"
        with self.assertRaises(RandomSourceError) as context:
            a = RandomList('all')
        self.assertEqual(type(context.exception), RandomSourceError, "wrong exception type")

    def test_09_bad_size(self):
        "First argument must be an integer or 'all'"
        with self.assertRaises(RandomSourceError) as context:
            a = RandomList('foo','fish')
        self.assertEqual(type(context.exception), RandomSourceError, "wrong exception type")

    def test_10_too_many_fish(self):
        "Can't make a set with more than the number of items in the data file"
        with self.assertRaises(RandomSourceError) as context:
            a = RandomList(100,'fish')
        self.assertEqual(type(context.exception), RandomSourceError, "wrong exception type")

    def test_11_unknown(self):
        "Making a list from an unknown data source"
        with self.assertRaises(RandomSourceError) as context:
            a = RandomList(100,'flowers')
        self.assertEqual(type(context.exception), RandomSourceError, "wrong exception type")
        
    # Test the random() method on lists of integers and lists of strings

    def test_12_random_int(self):
        "Test random('success') and random('fail') for lists of integers"
        a = RandomList(10)
        for i in range(0,5):
            x = a.random('success')
            self.assertTrue(x in a, "random('success') isn't in list")
            x = a.random('fail')
            self.assertFalse(x in a, "random('fail') is in list")
            self.assertTrue(type(x) == int, "random('fail') isn't an integer")

    def test_13_random_fish(self):
        "Test random('success') and random('fail') for lists of fish"
        a = RandomList(10, 'fish')
        allfish = RandomList('all','fish')
        for i in range(0,5):
            x = a.random('success')
            self.assertTrue(x in a, "random('success') isn't in list")
            x = a.random('fail')
            self.assertFalse(x in a, "random('fail') is in list")
            self.assertTrue(x in allfish, "random('fail') isn't a fish")
            
    # Add test with sorted=True

