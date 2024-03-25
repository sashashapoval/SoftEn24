import unittest

from PythonLabs.SieveLab import *

class SieveTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nSieveLab:  ", end = "")
        
    def setUp(self):
        self.worksheet = [None,None] + list(range(2,30))
        self.primes = [2,3,5,7,11,13,17,19,23,29]
        
    def test_03_sieve(self):
        "make a list of prime numbers less than 30"
        a = sieve(30)
        self.assertEqual(self.primes, a, "sieve(30) failed")
        
    def test_04_pi(self):
        "π(n) is the number of primes less than n; test for n = 10, 100, 1000, and 10000"
        pi = [0, 4, 25, 168, 1229]
        for i in range(1,len(pi)):
            self.assertEqual(pi[i], len(sieve(10**i)), "π[%d] failed" % i)

