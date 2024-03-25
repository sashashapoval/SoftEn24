import unittest

from PythonLabs.RandomLab import *

class RandomTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nRandomLab:  ", end = "")
        
    # The prng_sequence method makes a sequence of numbers using a linear congruential
    # method with the specified a, c, and m values

    def test_01_prng_sequence(self):
        sched8 = prng_sequence(1, 8, 12)
        self.assertEqual(12, len(sched8), "expected 12 items")
        self.assertEqual(3, len(set(sched8)), "exptected 3 unique items")

        sched7 = prng_sequence(1, 7, 12)
        self.assertEqual(12, len(sched7), "expected 12 items")
        self.assertEqual(12, len(set(sched7)), "exptected 12 unique items")

        seq1 = prng_sequence(3, 337, 1000)
        self.assertEqual([0, 337, 348, 381], seq1[0:4], "first four numbers are wrong")
        self.assertEqual(100, len(set(seq1)), "exptected 100 unique items")

        seq2 = prng_sequence(81, 337, 1000)
        self.assertEqual([0, 337, 634, 691], seq2[0:4], "first four numbers are wrong")
        self.assertEqual(1000, len(set(seq2)), "exptected 1000 unique items")

    # A PRNG object generates the same sequence of values as the prng_sequence method,
    # but makes them on demand.  Test the sequence, test resetting the seed, test again.
    # Also tests the random(n,m) method, which maps a sequence value to n..m

    def test_02_PRNG(self):
        p = PRNG(81, 337, 1000)
        self.assertEqual(0, p.state(), "sequence not initialized to 0")
        self.assertEqual(337, p.advance(), "wrong first value")
        self.assertEqual(634, p.advance(), "wrong second value")

        p.seed(0)
        self.assertEqual(0, p.state(), "call to seed didn't reset sequence")
        self.assertEqual(337, p.advance())
        self.assertEqual(634, p.advance())

        p.seed(0)
        self.assertEqual(2, p.randint(1,6), "wrong value from randint")     #  (337 % 6) + 1
        self.assertEqual(5, p.randint(1,6), "wrong value from randint")     #  (634 % 6) + 1

    # For the Card tests, a call to the Card constructor with an integer argument 
    # makes a specified card; 0 = 2 ♣ and ending with 51 = A ♠.

    def test_03_cards(self):
        c1 = Card(0)
        # self.assertEqual('2', c1.rank(), "first card isn't a 2")
        # self.assertEqual('♣', c1.suit(), "first card isn't a club")
        self.assertEqual(0, c1.rank(), "first card isn't a 2")
        self.assertEqual(0, c1.suit(), "first card isn't a club")
        self.assertEqual('2♣', str(c1), "first card isn't the 2 of clubs")

        c2 = Card(51)
        # self.assertEqual('A', c2.rank(), "second card isn't an ace")
        # self.assertEqual('♠', c2.suit(), "second card isn't a spade")
        self.assertEqual(12, c2.rank(), "second card isn't an ace")
        self.assertEqual(3, c2.suit(), "second card isn't a spade")
        self.assertEqual('A♠', str(c2), "second card isn't the ace of spades")

    # Make a full deck, make sure every card is present.  Then shuffle the deck,
    # check again.  Sort the shuffled deck, make sure all cards are there and in
    # order.

    def test_04_deck(self):
        d1 = [Card(i) for i in range(0,52)]
        self.check_all_cards(d1)
        d2 = [Card(i) for i in range(0,52)]
        permute(d2)
        self.check_all_cards(d2)
        d2.sort()
        self.assertEqual(d1, d2, "deck wasn't sorted")
        
    # Helper called by deck test

    def check_all_cards(self, deck):
        "Make sure a deck as 52 cards, 13 in each suit and 4 of each rank."

        ranklist = [c.rank() for c in deck]
        ranks = set(ranklist)
        self.assertEqual(13, len(ranks), "deck doesn't have all 13 ranks")
        for r in ranks:
            self.assertEqual(4, ranklist.count(r), "didn't find 4 %s's" % r)

        suitlist = [c.suit() for c in deck]
        suits = set(suitlist)
        self.assertEqual(4, len(suits), "deck doesn't have all 4 suits")
        for s in suits:
            self.assertEqual(13, suitlist.count(s), "didn't find 13 %s's" % s)

        pass

    # Test histogram objects

    def test_05_histograms(self):
        # a histogram for counting rolls of a die
        h = Histogram(range(1,7))
        self.assertEqual(6, len(h), "histogram should have 6 bins")
        for i in range(1,7):
            self.assertEqual(0, h[i], "bin isn't 0")
        h.count(1)
        self.assertEqual(1, h[1], "bin 1 wasn't incremented")
        h.count(6)
        self.assertEqual(1, h[6], "bin 6 wasn't incremented")

        # a histogram with string labels
        a = ['fee', 'fie', 'foe', 'fum']
        h = Histogram(a)
        self.assertEqual(len(a), len(h), "histogram should have one bin for each array element")
        for x in a:
            self.assertEqual(0, h[x], "bin isn't 0")
        h.count('fie')
        self.assertEqual(1, h['fie'], "bin wasn't incremented")
        
        # a histogram with 10 bins for values between 0 and 99
        h = Histogram(10, 100)
        self.assertEqual(10, len(h), "histogram should have 10 bins")
        for i in range(10):
            self.assertEqual(0, h[i], "bin isn't 0")
        # check value in middle and also extreme values
        h.count(42)
        self.assertEqual(1, h[4], "bin wasn't incremented")
        h.count(0)
        self.assertEqual(1, h[0], "bin wasn't incremented")
        h.count(99)
        self.assertEqual(1, h[9], "bin wasn't incremented")
        with self.assertRaises(KeyError) as context:
            h.count(-1)
        self.assertEqual(type(context.exception), KeyError, "-1 should be outside range 0..99")
        with self.assertRaises(KeyError) as context:
            h.count(100)
        self.assertEqual(type(context.exception), KeyError, "100 should be outside range 0..99")


    # Test poker hands

    # def test_06_poker(self):
    #     self.assertEqual(poker_rank(self.deal([0,1,2,3,4])),     Poker.straight_flush)
    #     self.assertEqual(poker_rank(self.deal([0,13,26,39,1])),  Poker.four_of_a_kind)
    #     self.assertEqual(poker_rank(self.deal([0,13,26,1,14])),  Poker.full_house)
    #     self.assertEqual(poker_rank(self.deal([0,2,4,6,8])),     Poker.flush)
    #     self.assertEqual(poker_rank(self.deal([0,14,2,3,4])),    Poker.straight)
    #     self.assertEqual(poker_rank(self.deal([0,13,26,1,15])),  Poker.three_of_a_kind)
    #     self.assertEqual(poker_rank(self.deal([0,13,1,14,15])),  Poker.two_pair)
    #     self.assertEqual(poker_rank(self.deal([0,13,1,2,3])),    Poker.pair)
    #     self.assertEqual(poker_rank(self.deal([0,14,29,44,45])), Poker.high_card)
    
    def test_06_poker(self):
        self.assertEqual(poker_rank(self.deal([0,1,2,3,4])),     'straight flush')
        self.assertEqual(poker_rank(self.deal([0,13,26,39,1])),  'four of a kind')
        self.assertEqual(poker_rank(self.deal([0,13,26,1,14])),  'full house')
        self.assertEqual(poker_rank(self.deal([0,2,4,6,8])),     'flush')
        self.assertEqual(poker_rank(self.deal([0,14,2,3,4])),    'straight')
        self.assertEqual(poker_rank(self.deal([0,13,26,1,15])),  'three of a kind')
        self.assertEqual(poker_rank(self.deal([0,13,1,14,15])),  'two pair')
        self.assertEqual(poker_rank(self.deal([0,13,1,2,3])),    'pair')
        self.assertEqual(poker_rank(self.deal([0,14,29,44,45])), 'high card')
    
    # Helper function called by poker test -- make a hand with specified card numbers
    
    def deal(self, a):
      return [ Card(n) for n in a ]
        