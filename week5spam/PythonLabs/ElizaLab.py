# Python implementation of Joseph Weizenbaum's ELIZA program

import PythonLabs
from .Tools import PQBase, classname, path_to_data
from copy import copy
import os
import re
from warnings import warn
from random import randint

class ElizaError(Exception):  pass

class Pattern:
    """
    [ElizaLab]  A Pattern represents one way to transform an input sentence into a
    response.  A Pattern instance has a regular expression and a list of one or more 
    reassembly strings that can refer to groups in the expression.  There is also an 
    index to record the last reassembly string used, so the application can cycle 
    through the strings.
    """
    
    # # These two attributes serve as "global" variables, needed to pass arguments
    # # to the functions called from re.sub :-(  May be set to other values just
    # # before a call to Eliza._placeholder to substitute substrings from the input
    # # into the response
    # 
    # groups = None
    # postprocessor = None
    
    def __init__(self, expr, responses = []):
        """
        Create a new sentence pattern that will apply to input sentences that
        match expr.  To make it easier for users to create patterns without knowing 
        too many details of regular expressions the constructor modifies expr:
           add "anchors" so words in the pattern do not match partial words from inputs
           add parentheses around ".*" and "$n" to capture parts of the input string
           add parentheses around groups of words, e.g. "a|b|c"
        """
        expr = Pattern._add_parens(expr, r'\(?\.\*\)?')                     # add parens around .*
        expr = Pattern._add_parens(expr, r'\(?[\w\' ]+(\|[\w\' ]+)+\)?')    # add parens around alternatives
        expr = Pattern._add_parens(expr, r'\(?\$\w+\)?')                    # add parens around variable names
        if re.search(r'^\w', expr):
            expr = r'\b' + expr 
        if re.search(r'\w$', expr):
            expr = expr + r'\b' 
        self._expr = expr
        self._responses = copy(responses)
        self._index = 0
        
    def __repr__(self):
        return "<%s '%s'>" % (classname(self), self.expr())
        # return "  /" + self._expr + "/\n" + '\n'.join([("    %s" % resp) for resp in self._responses])
        
    def expr(self):
        return self._expr.replace(r'\b', '')
    
    def match(self, s):
        """
        Return True if this pattern matches sentence s.
        """
        m = re.search(self._expr, s, re.IGNORECASE)
        return m != None

    def apply(self, s, pre = None, post = {}):
        """
        Try to apply this pattern to input sentence s.  If s matches the regular
        expression for this pattern extract the parts that match groups, insert them
        into the next response string, and return the result.  If  does not match
        the regular expression return None.  The pre and post arguments are optional
        dictionaries used for preprocessing and postprocessing substitutions
        (this preprocessing step is only used by unit tests and interactive demos; 
        the top level Eliza.run function does its own preprocessing).
        """
        if pre != None:
            s = Eliza.preprocess(s, pre)
        m = re.search(self._expr, s, re.IGNORECASE)
        if m == None or len(self._responses) == 0:
            return None
        resp = self._responses[self._index]
        self._index = (self._index + 1) % len(self._responses)
        if resp[0] == '@':
            return resp
        if Eliza.verbose:  print("Reassembling '%s'" % resp)
        Pattern.groups = m.groups()             # save match results for _placeholder() to use
        Pattern.post = post                     # save postprocessing dictionary for _placeholder()
        resp = re.sub(r'\$\d+', Pattern._placeholder, resp)
        return resp
        
    def reset(self):
        "Set the internal pointer to the first response string."
        self._index = 0
        
    def add_response(self, s):
        "Append sentence s to the list of response strings for this pattern."
        self._responses.append(s)
        
    def responses(self):
        return self._responses
            
    @staticmethod
    def _add_parens(s, r):
        """
        Helper function called by the constructor -- add parentheses around every occurrence
        of the string r in sentence pattern s unless there are already parentheses there.
        """
        return re.sub(r, Pattern._check_parens, s)
        
    @staticmethod
    def _check_parens(m):
        "Helper function -- parenthesize match m if it's not already parenthesized"
        if m.group(0)[0] == '(' and m.group(0)[-1] == ')':
            return m.group(0)
        else:
            return "(" + m.group(0) + ")"
            
    @staticmethod
    def _placeholder(m):
        """
        Match object m contains a string of the form $n.  Get the corresponding piece of
        the input sentence, apply postprocessing rules, and return the result.  If there
        weren't n groups in the pattern return $n unchanged.
        """
        n = int(m.group(0)[1:]) - 1
        if n >= len(Pattern.groups):
            return('$' + str(n))
        before = Pattern.groups[n]
        after = re.sub(Eliza.word, Pattern._replaceword, before)
        if Eliza.verbose:  print("  postprocess '%s' => '%s'" % (before,after))
        return after

    @staticmethod
    def _replaceword(m):
        "Helper function called by _placeholder to look up a word in a postprocessing dictionary"
        word = m.group(0)
        if word in Pattern.post:
            return Pattern.post[word]
        else:
            return word

class Rule:
    """
    A transformation rule is associated with a key word, and is triggered
    when that word is found in an input sentence.  Rules have integer
    priorities, and if more than one rule is enabled Eliza applies the one
    with the highest priority.  

    Each rule has an ordered list of patterns which control how Eliza will
    respond to sentences containing the key word (see the Pattern class).
    """
    def __init__(self, name, priority = 1):
        self._name = name
        self._priority = priority
        self._patterns = [ ]
        
    def __repr__(self):
        a = []
        for p in self._patterns:
            a.append("'" + p.expr() + "'")
        return classname(self) + " " + str([self._priority]) + "\n   " + "\n   ".join(a)
        
    def __lt__(self, other):
        "This rule goes ahead of another rule in the queue if it has a higher or same priority."
        return self._priority >= other._priority
        
    def __getitem__(self, i):
        "Return pattern number i from this rule's list of patterns."
        return self._patterns[i]
        
    def name(self):
        "Accessor method: return the rule's name."
        return self._name
        
    def add_pattern(self, p):
        """
        Add a Pattern object for the string p to the list of patterns recognized by this rule.
        If the string is delimited by / characters (i.e. the pattern was read from a script
        file) remove them.
        """
        p = p.strip('/')
        self._patterns.append(Pattern(p))
        
    def patterns(self):
        return self._patterns
        
    def add_reassembly(self, s):
        """
        Add s to the list of reassembly strings for the current pattern (the one most recently
        added to the pattern list)
        """
        self._patterns[-1].add_response(s)
        
    def apply(self, s, pre = None, post = None):
        """
        Apply this rule to a sentence s.  Try the patterns in order, returning the string
        generated by the first pattern that returns something other than None.  Return None
        if no pattern matches.
        """
        for p in self._patterns:
            if Eliza.verbose:  print("  /%s/" % p._expr)
            res = p.apply(s, pre = pre, post = post)
            if res:  return res
        return None
        
class Lexicon(dict):
    """
    [ElizaLab] A Lexicon object is basically just a case-insensitive dictionary, e.g. when
    evaluating the expression d[x] convert key x to lower case letters so d["a"] and d["A"]
    both return the same value.
    """
    def __init__(self):
        super().__init__()
        
    def __getitem__(self, key):
        return super().__getitem__(key.lower())
        
    def __setitem__(self, key, val):
        super().__setitem__(key.lower(), val)
        
    def __contains__(self, key):
        return super().__contains__(key.lower())


class PriorityQueue(PQBase):
    """
    [ElizaLab] A PriorityQueue is an ordered collection of items.  Add items by calling
    insert, remove the first item by calling pop.
    """
    def __init__(self):
        "[ElizaLab] Create a new priority queue, initially empty."
        super().__init__()
        
    def insert(self, item):
        "In this derived class insert makes sure there are no duplicates."
        if item not in self._q:
            super().insert(item)

class Eliza:
    """
    [ElizaLab] A Python implementation of Joseph Weizenbaum's classic ELIZA program.
    Top level functions are called by preceding the function name with the module
    name, e.g. Eliza.load(script), Eliza.run(), etc.
    """

    def __init__(self):
        """don't do this"""
        raise ElizaError("Eliza is a singleton object")

    # These state variables are accessible by any functions and classes defined 
    # inside the ElizaLab module

    verbose = False
    pre = Lexicon()
    post = Lexicon()
    rules = Lexicon()
    var = r'\$\d+'              # variable name in reassembly string
    word = r'[\w\-$\']+'        # pattern for a "word" in the input language
    punctuation = ',.?!:;-'     # chars to strip from words when scanning sentences

    def clear():
        """docstring for clear"""
        Eliza.script = None
        Eliza.aliases = { }
        Eliza.vars = { }
        Eliza.starts = [ ]
        Eliza.stops = [ ]
        Eliza.queue = PriorityQueue()

        Eliza.verbose = False
        Eliza.pre.clear()
        Eliza.post.clear()
        Eliza.rules.clear()

        Eliza.default = Rule(':default')
        Eliza.default.add_pattern(r'(.*)')
        Eliza.default.add_reassembly("$1")
        
    def load(filename):
        """
        Get all the lines from a script file and pass them to Eliza.compile
        to turn into Rule and Pattern objects.
        """
        with open(filename) as scriptfile:
            script = scriptfile.readlines()
        Eliza.compile(script)
        Eliza.script = filename
        
    def compile(script):
        """
        Create Rule objects based on each line in the script.  Called by Eliza.load
        after reading a script from an input file and from unit tests or interactive
        sessions that experiment with rules.
        """
        Eliza.clear()
        Eliza.current_rule = None
        for line in script:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':  continue
            if line[0] == ':':
                Eliza._parse_directive(line)
            else:
                Eliza._parse_line(line)
        Eliza._compile_rules()
        
    def info():
        """
        Print information about the current script.
        """
        words = set()
        npatterns = 0
        
        for (name,rule) in Eliza.rules.items():
            if name[0] != '$': words.add(name.lower())
            for p in rule._patterns:
                npatterns += 1
                for parts in p._expr.split():
                    Eliza._add_info(parts, words)
                    
        for k in Eliza.aliases:
            words.add(k.lower())
        
        print("Script: ", Eliza.script)
        print("  %d rules with %d sentence patterns" % (len(Eliza.rules), npatterns))
        print("  %d key words: %s" % (len(words), sorted(words)))
        
    def _add_info(s, words):
        "Helper function for Eliza.info() -- extract key words from a regular expression"
        if s.startswith(r'\b'): s = s[2:]
        if s.endswith(r'\b'): s = s[:-2]
        s = re.sub('\(', '', s)
        s = re.sub('\)', '', s)
        s = re.sub('\.\*', '', s)
        s = re.sub('\?', '', s)
        if len(s) == 0: 
            return
        for w in s.split('|'):
            words.add(w.lower())

    def run():
        """
        Top level method to carry on a conversation.  Starts a read-eval-print loop,
        stopping when the user types "bye" or "quit".  For each input sentence, call
        Eliza.transform to find a rule that applies to the sentence and print the
        response.
        """
        if len(Eliza.starts) > 0:
            print(Eliza.starts[randint(0,len(Eliza.starts)-1)])
        while True:
            sentence = input("  H: ")
            if sentence == 'bye' or sentence == 'quit':
                break
            if Eliza.verbose:  print("----------------")
            response = Eliza.transform(sentence)
            if Eliza.verbose:  print("----------------")
            print("  C: " + response)

    def transform(sentence):
        """
        The transform method is called by the top level Eliza.run method to process
        each sentence typed by the user.  Initialize a priority queue, apply
        preprocessing transformations, and add rules for each word to the queue.  Then apply
        the rules, in order, until a call to r.apply() for some rule r returns a
        non-empty response.  Note that the default rule should apply to any input string, so
        it should never be the case that the queue empties out before some rule can apply.
        """
        Eliza.queue.clear()
        Eliza.queue.insert(Eliza.default)

        sentence = sentence.strip(Eliza.punctuation)
        sentence = Eliza.preprocess(sentence, Eliza.pre)
        Eliza.scan(sentence)
        if Eliza.verbose:  print("Queue:", [rule.name() for rule in Eliza.queue])
        
        while len(Eliza.queue) > 0:
            rule = Eliza.queue.pop()
            result = Eliza.apply(rule, sentence)
            if result:
                return result
        return ""                   # <-- should never get here...
     
    def preprocess(sentence, pre):
        "Apply the preprocessing rules in pre to the input sentence, return the result"
        if Eliza.verbose:  print("Preprocessing...\n  before: '%s'" % sentence)
        sentence = re.sub(r'\s+', " ", sentence)
        Eliza.pre_arg = pre         # value passed to _prehelper
        res = re.sub(Eliza.word, Eliza._prehelper, sentence)
        if Eliza.verbose:  print("  after:  '%s'" % res)
        return res

    def _prehelper(m):
        word = m.group(0)
        if word in Eliza.pre_arg:
            return Eliza.pre_arg[word]
        else:
            return word
    
    def scan(sentence):
        """
        For each word in the input sentence (a) see if the word has a substitution in the
        preprocessing lexicon and (b) if there is a rule for the word add it to the queue.
        """
        msg = "Scanning... "
        for word in sentence.split():
            word = word.strip(Eliza.punctuation)
            msg = msg + word
            rule = Eliza.rule_for(word)
            if rule:
                Eliza.queue.insert(rule)
                msg = msg + "*"
            msg = msg + ", "
        if Eliza.verbose:  print(msg[0:-2])
        
    # def rule_for(word):
    #     """
    #     docstring for rule_for
    #     """
    #     if word in Eliza.rules:
    #         return Eliza.rules[word]
    #     elif word in Eliza.aliases:
    #         alias = Eliza.aliases[word]
    #         if alias in Eliza.rules:
    #             return Eliza.rules[alias]
    #     else:
    #         return None
    
    def rule_for(word):
        """
        docstring for rule_for
        """
        try:
            return Eliza.rules[word]
        except KeyError:
            try:
                return Eliza.rules[Eliza.aliases[word]]
            except KeyError:
                return None
        
    def apply(rule, sentence):
        """
        The apply method implements the second step in the "Eliza algorithm" to determine the 
        response to an input sentence.  It is called from the top level method (Eliza.transform) 
        to see if a rule applies to an input sentence.  If so, return the string generated by 
        the Rule object, otherwise return None.
        
        This is the method that handles indirection in scripts.  If a rule body has a line
        of the form "@x" it means sentences containing the rule for this word should be
        handled by the rule for x.  For example, suppose a script has this rule:
           duck
              /football/
                "I love my Ducks"
              /.*/
                @bird
        The rule will be added to the queue when an input sentence contains the word "duck".
        When Eliza applies the rule it will see if the sentence matches the pattern /football/, 
        i.e. if the word "football" appears anywhere else in the sentence, and if so respond 
        with the string "I love my Ducks".  If not, the next pattern succeeds (every input 
        matches .*) and the response is generated by the rules for "bird".
        """
        if Eliza.verbose:  print("Rule for '%s'" % rule.name())
        res = rule.apply(sentence, pre = None, post = Eliza.post)   # preprocessing already done by scan()
        if res and res[0] == '@':
            irule = Eliza.rule_for(res[1:])
            if irule:
                return Eliza.apply(irule, sentence)
            else:
                warn("No rule for %s" % rulename)
                return None
        else:
            return res

    def _parse_alias(line):
        if len(line) == 0 or line[0] != '$':
            warn("alias must be followed by a variable name")
        else:
            sym, line = line.split(None, 1)
            Eliza.vars[sym] = [ ]
            for word in line.split():
                Eliza.aliases[word] = sym
                Eliza.vars[sym].append(word)
        
    def _parse_start(line):
        Eliza.starts.append(line.strip('"'))
        
    def _parse_stop(line):
        Eliza.stops.append(line.strip('"'))

    def _parse_pre(line):
        try:
            sym, equiv = line.split(None, 1)
            Eliza.pre[sym] = equiv.strip('"')
        except ValueError:
            warn("missing string in :pre statement")

    def _parse_post(line):
        try:
            sym, equiv = line.split(None, 1)
            Eliza.post[sym] = equiv.strip('"')
        except ValueError:
            warn("missing string in :post statement")

    def _parse_default(line):
        name, *rest = line.split(None, 1)
        Eliza.default = name

    _directives = {
        ":alias" : _parse_alias,
        ":start" : _parse_start,
        ":stop" : _parse_stop,
        ":pre" : _parse_pre,
        ":post" : _parse_post,
        ":default" : _parse_default,
    }
        
    def _parse_directive(line):
        """docstring for _parse_directive"""
        cmnd, args = line.split(None,1)                 # get the first word from the line
        if cmnd in Eliza._directives:
            Eliza._directives[cmnd](args)
        else:
            warn("unknown directive: %s" % cmnd)
        Eliza.current_rule = None
        
    def _parse_line(line):
        """docstring for _parse_line"""
        if re.match(Eliza.word, line):                  # does the line start with a word?
            rulename, *priority = line.split()          # if so it's a rule name
            rule = Rule(rulename) if len(priority) == 0 else Rule(rulename, int(priority[0]))
            Eliza.rules[rulename] = rule
            Eliza.current_rule = rule
        elif Eliza.current_rule == None:                # make sure there is a rule to add stuff to
            warn("missing rule name?")
        elif line[0] == '/':
            if line[-1] == '/':
                Eliza.current_rule.add_pattern(line)
            else:
                warn("badly formed expression (missing /)")
        elif line[0] == '"':
            if line[-1] == '"':
                Eliza.current_rule.add_reassembly(line.strip('"'))
            else:
                warn("badly formed string (missing \")")
        elif line[0] == '@':
            Eliza.current_rule.add_reassembly(line)
        else:
            warn("unexpected line")

    def _compile_rules():
        """
        Check each pattern's regular expression and replace var names by alternation
        constructs.  If the script specified a default rule name look up that
        rule and save it as the default.
        """
        for (name,rule) in Eliza.rules.items():
            for p in rule._patterns:
                p._expr = re.sub(r'\$\w+', Eliza._join_aliases, p._expr)
        if type(Eliza.default) == str and Eliza.default in Eliza.rules:
            Eliza.default = Eliza.rules[Eliza.default]
            
    def _join_aliases(m):
        "Helper called by _compile_rules to make an expression that matches all aliases for a variable"
        return("|".join(Eliza.vars[m.group(0)]))
        
# After defining all the classes and functions call Eliza.clear() to set the
# initial values for the default script.

Eliza.clear()
        
         
