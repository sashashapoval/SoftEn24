import unittest

from PythonLabs.SpamLab import *

class SieveTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nSpamLab:  ", end = "")
                
    def setUp(self):
        self.pgood = load_probabilities(path_to_data('good.txt'))
        self.pbad = load_probabilities(path_to_data('bad.txt'))

    def test_01_data(self):
        "check some expected probabilities"
        self.assertAlmostEqual(self.pgood['spam'], 0.0101)
        self.assertAlmostEqual(self.pbad['spam'], 0.002)
        self.assertIn('cadet', self.pgood)
        self.assertNotIn('cadet', self.pbad)
        self.assertNotIn('tantrum', self.pgood)
        self.assertIn('tantrum', self.pbad)
        
    def test_02_spamicity(self):
        "test the spamicity function"
        self.assertAlmostEqual(spamicity('diet', self.pbad, self.pgood), 0.8275862068965517)
        self.assertAlmostEqual(spamicity('iterate', self.pbad, self.pgood), 0.04000000000000001)
        self.assertIsNone(spamicity('hobbit', self.pbad, self.pgood))

    def test_03_pspam(self):
        "test the pspam function"
        self.assertAlmostEqual(pspam(path_to_data('msg1.txt'), vis = 0), 0.9293048326577117)
        self.assertAlmostEqual(pspam(path_to_data('msg4.txt'), vis = 0), 3.758445064217253e-15)

