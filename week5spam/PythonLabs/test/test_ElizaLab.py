import unittest

from PythonLabs.ElizaLab import *

class ElizaTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nElizaLab:  ", end = "")
        
    # A Pattern object represents a sentence pattern, which associates a regular
    # expression with a set of possible responses.

    # The simplest pattern has a literal word, and cycles through sentences when applied
    # to inputs that contain that word

    def test_01_literal(self):
        p = Pattern("father", ["yes", "no"])
        self.assertTrue(p.match("father knows best"), "sentence did not match pattern")
        self.assertEqual("yes", p.apply("father knows best"), "wrong response")
        self.assertEqual("no", p.apply("father knows best"), "wrong response")
        self.assertEqual("yes", p.apply("father knows best"), "wrong response")
        self.assertIsNone(p.apply("who's your daddy"), "sentence should not match pattern")
        
    # Literals in a pattern are bracketed by \b anchors

    def test_02_anchors(self):
        p = Pattern("father", ["yes"])
        self.assertIsNone(p.apply("he is a grandfather"))
        self.assertEqual("yes", p.apply("my father-in-law"))
        self.assertIsNone(p.apply("land of my fathers"))

    # Test the add_response method

    def test_03_add_response(self):
        p = Pattern("father")
        p.add_response("one")
        p.add_response("two")
        self.assertEqual("one", p.apply("father knows best"))
        self.assertEqual("two", p.apply("my father-in-law"))

    # Test word groups

    def test_04_groups(self):
        p = Pattern("father|mother")
        self.assertTrue(p.match("father knows best"))
        self.assertTrue(p.match("my mother the car"))

    # Match parts used in responses

    def test_05_match_parts(self):
        p = Pattern("I (like|love|adore) my (dog|cat|ducks)")
        p.add_response("You $1 your $2?")
        pp = { 'your' : 'my' }
        self.assertEqual("You like your cat?", p.apply("I like my cat", post = pp))
        self.assertEqual("You love your ducks?", p.apply("I love my ducks", post = pp))

    # Wild card pattern

    def test_06_wildcard(self):
        p = Pattern("I like (.*)")
        p.add_response("Why do you like $1?")
        pp = { 'your' : 'my' }
        self.assertEqual("Why do you like to drink beer?", p.apply("I like to drink beer", post = pp))
        self.assertEqual("Why do you like that car?", p.apply("I like that car", post = pp))

    # Postprocessing

    def test_07_postprocess(self):
        p = Pattern("I am (.*)")
        p.add_response("Are you really $1?")
        pp = {"I" : "you", "your" : "my"}
        self.assertEqual("Are you really afraid of your dog?", p.apply("I am afraid of your dog"))
        self.assertEqual("Are you really afraid of my dog?", p.apply("I am afraid of your dog", post = pp))
        self.assertEqual("Are you really sorry you dropped my computer?", p.apply("I am sorry I dropped your computer", post = pp))

    # Preprocessing

    def test_08_preprocess(self):
        p = Pattern("I am (.*)")
        p.add_response("Are you really $1?")
        self.assertIsNone(p.apply("I'm sorry"))
        self.assertEqual("Are you really sorry?", p.apply("I'm sorry", pre = {"I'm" : "I am"}))

    # Case insensitive matches

    def test_09_case(self):
        p = Pattern("I am (.*)")
        p.add_response("Are you really $1?")
        pp = Lexicon()
        pp["I'm"] = "I am"
        self.assertEqual("Are you really sorry?", p.apply("i am sorry"))
        self.assertEqual("Are you really sorry?", p.apply("i'm sorry", pre = pp))
        
    ## NOTE: the following tests depend on rules defined in the 'doctor' script
    ## distributed with the labs and may have to be updated if the script changes...
    
    def test_10_no_rule(self):
        Eliza.load(path_to_data('doctor.txt'))
        self.assertEqual("I am not sure I understand you fully.", Eliza.transform("Time flies"))

    def test_11_simple_rule(self):
        Eliza.load(path_to_data('doctor.txt'))
        self.assertEqual("How do you do? Please state your problem.", Eliza.transform("Hello"))

    def test_12_high_priority_rule(self):
        Eliza.load(path_to_data('doctor.txt'))
        self.assertEqual("Do computers worry you?", Eliza.transform("I don't trust computers"))

    def test_13_preprocess(self):
        Eliza.load(path_to_data('doctor.txt'))
        self.assertEqual("How do you know you can't do it?", Eliza.transform("I can't do it"))

    def test_14_postprocess(self):
        Eliza.load(path_to_data('doctor.txt'))
        self.assertEqual("Why are you concerned over my hat?", Eliza.transform("I like your hat"))

    def test_15_indirection(self):
        Eliza.load(path_to_data('doctor.txt'))
        self.assertEqual("In what way?", Eliza.transform("Love is like oxygen"))


          
