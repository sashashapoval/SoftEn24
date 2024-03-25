# Common classes, functions used by several lab modules

__all__ = [
    "PQBase", "Counter", "RandomList", "RandomSourceError", 
    "log2", "classname", "enum", 
    "path_to_data", "tokenize", 
    "prefix", "suffix", "randnoun", "randverb",
    "hello",
]

import PythonLabs
from random import randint
import os
import re
import string
from copy import deepcopy

## A function users can call to test their installation

def hello(w = 200, h = 100, size = 10, graphic = False):
    "Verify PythonLabs and Tk are installed"
    from PythonLabs.Canvas import Canvas, tk
    try:
        Canvas.init(w, h, "PythonLabs Canvas")
        if graphic:
            Canvas.Rectangle(0, 0, size, size, fill='blue', width=0)
            Canvas.Rectangle(0, h-size, size, h, fill='blue', width=0)
            Canvas.Rectangle(w, 0, w-size, size, fill='blue', width=0)
            Canvas.Rectangle(w, h, w-size, h-size, fill='blue', width=0)
            Canvas.Rectangle((w-size)/2, (h-size)/2, size+(w-size)/2, size+(h-size)/2, fill='blue', width=0)
        else:
            Canvas.Text('Hello!', w/2, h/2, anchor=tk.CENTER)
    except Exception as e:
        print("PythonLabs cannot connect to Tk:\n  ", e)

    print("PythonLabs is installed")


## Priority Queue Base

class PQBase:
    """
    [PythonLabs] A priority queue is an ordered sequence, similar to a list, except items
    can only be added by calling the insert method, which adds a single item so the queue
    remains sorted, and can only be removed by calling pop, which removes a single item 
    from the front.  This class defines the base functionality of a priority queue; labs
    such as BitLab and ElizaLab will define their own PriorityQueue classes as extensions
    of PQBase.
    """
    def __init__(self):
        self._q = []
        
    def __repr__(self):
        return "[" + ", ".join(map(str,self._q)) + "]"
        
    def __len__(self):
        "[PythonLabs] Return the number of items in this queue"
        return len(self._q)

    def insert(self, x):
        "[PythonLabs] Add an item to this queue, keeping the queue sorted"
        i = 0
        while i < len(self._q):
            if x < self._q[i]: break
            i += 1
        self._q.insert(i, x)
        return self
    
    def pop(self):
        "[PythonLabs] Remove the first item from this queue"
        if len(self._q) > 0:
            return self._q.pop(0)
        else:
            return None
            
    def clear(self):
        " [PythonLabs] Delete all items in this queue."
        self._q = []
            
    def __getitem__(self, x):
        "[PythonLabs] Access individual items in this queue"
        return self._q[x]
        
    def __iter__(self):
        "[PythonLabs] Iterate over all items in this queue"
        for x in self._q:
            yield x

## Event counter

class Counter:
    
    counters = {}
    
    @staticmethod
    def reset(name):
        Counter.counters[name] = 0
        
    @staticmethod
    def increment(name):
        if name in Counter.counters:
            Counter.counters[name] += 1
        else:
            print("Warning: uninitialized counter: " + str(name) + " (ignored)")
        
    @staticmethod
    def value(name):
        if name in Counter.counters:
            return Counter.counters[name]
        else:
            return None

    @staticmethod
    def dump(name = None):
        if name == None:
            for x in Counter.counters:
                print("%s: %d" % (x, Counter.counters[x]))
        else:
            print("%s: %d" % (name, Counter.counters[name]))

## RandomList

class RandomList(list):
    "[PythonLabs] A list of random items used to test searching and sorting algorithms"
    
    _sources = ('cars', 'colors', 'elements', 'fruits', 'fish', 'languages', 'words', 'nouns', 'verbs')
        
    def __init__(self, size, arg2 = None, sorted=False):
        if type(size) == int:
            if arg2 == None:
                self._max = 100 if size < 50 else 10 * size
            elif type(arg2) == int:
                if arg2 < 2*size:
                    raise RandomSourceError("max must be at least 2x larger than size")
                else:
                    self._max = arg2
            else:
                self._max = 0
            self._all = False
        elif size == 'all':
            if arg2 == None or type(arg2) == int:
                raise RandomSourceError("can't make a list of all integers!")
            self._all = True
            self._max = 0
        else:
            raise RandomSourceError("size must be an integer or 'all'")
                        
        self._values = set()

        if (self._max > 0):
            while len(self._values) < size:
                r = randint(0,self._max-1)
                if not r in self._values:
                    self._values.add(r)
                    self.append(r)
        elif arg2 in RandomList._sources:
            filename = os.path.join(PythonLabs.datadir,'testsets',arg2+'.txt')
            with open(filename) as wordfile:
                self._words = wordfile.readlines()
            nwords = len(self._words)
            if self._all:
                for w in self._words:
                    self.append(w.strip())
            elif size > (nwords - 1):
                raise RandomSourceError("max " + str(nwords-1) + " items from " + arg2)
            else:
                while len(self._values) < size:
                    r = randint(0,nwords-1)
                    w = self._words[r].strip()
                    if not w in self._values:
                        self._values.add(w)
                        self.append(w)
        else:
            raise RandomSourceError("undefined source")
        
        if sorted:
            self.sort()

    def random(self, arg = 'success'):
        if arg == 'success':
            return self[ randint(0, len(self)-1) ]
        elif arg == 'fail':
            if self._all:
                raise RandomSourceError("all values are in the set")
            else:
                while True:
                    if self._max > 0:
                        x = randint(0, self._max-1)
                    else:
                        x = self._words[ randint(0, len(self._words)-1) ].strip()
                    if not x in self._values: break
                return x
        else:
            raise RandomSourceError("argument must be 'success' or 'fail'")
    
    def clone(self):
        return deepcopy(self)
        
    @staticmethod
    def sources():
        return RandomList._sources

class RandomSourceError(Exception): pass

## Miscellaneous Functions

from math import log

def log2(x):
    "[PythonLabs] Compute the logaritm (base 2) of x."
    return log(x) / log(2.0)

def classname(obj):
    "[PythonLabs] Create a string with the module name and class name of object x."
    return obj.__class__.__module__ + '.' + obj.__class__.__name__
    
def path_to_data(file):
    if file in PythonLabs.datafile:
        return PythonLabs.datafile[file]
    else:
        raise DataFileError("file not in the PythonLabs data directory")
        
class DataFileError(Exception): pass


## String Functions

def tokenize(s):
    "Split a string into tokens, converted to lower case and with punctuation removed"
    a = [ ]
    for x in s.split():
        a.append( x.strip(string.punctuation).lower() )
    return a

def prefix(s, n = -1):
    "Return the first characters of string s"
    if n == -1:
        n = len(s) - 1
    return s[:n]
    
def suffix(s, n = -1):
    "Return the last characters of string s"
    if n == -1:
        n = 1
    return s[-n:]
    
nouns = [ ]
verbs = [ ]

def randword(a, source):
    """Helper function called by randnoun or randverb, initializes a word list if needed,
    returns a random item from the list."""
    if len(a) == 0:
        a[:] = RandomList('all', source)
    return a[randint(0,len(a))]
    
def randnoun():
    """Return a random word from the list of common English nouns"""
    return randword(nouns, "nouns")

def randverb():
    """Return a random word from the list of common English verbs"""
    return randword(verbs, "verbs")

## Enumerated Types

def enum(name, *alist, **adict):
    """
    [PythonLabs] Create a new enumerated type with names taken from the list
    and dictionary arguments.  Names in the list are assigned unique integer
    values starting with 0.

    Example:
        >>> colors = enum('colors', 'red', 'green', 'blue', black = 99)
        >>> colors.red
        0
        >>> colors.black
        99
        >>> colors
        <class 'PythonLabs.Tools.colors'>
    """
    symbols = dict(zip(alist, range(len(alist))))
    symbols.update(adict)
    return type(name, (), symbols)

