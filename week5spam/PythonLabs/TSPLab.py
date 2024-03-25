# A genetic algorithm for the Traveling Salesman Problem

# __all__ = []

import PythonLabs
from .Tools import RandomList, classname, path_to_data
from .Canvas import Canvas
import os
from copy import copy
from random import random, randint
from math import sqrt, fsum, ceil
from functools import reduce

class TSPError(Exception):  pass

# Convenience

def summary(pop):
    return [int(t.cost()) if t is not None else None for t in pop]

# Combinations and permutations

def factorial(n):
    "Compute the factorial of n:  n * (n-1) * (n-2) * ... 1."
    from operator import mul
    return reduce(mul, range(1,n+1))

def ntours(n):
    "Compute the number of unique tours on a map with n cities."
    return factorial(n-1) // 2
    
def each_permutation(a):
    """
    Generate all permutations of iterable object a.  If a is a string the output will
    be a sequence of strings made from all possible orderings of the characters in a.
    If a is a list or tuple the output will be a sequence of tuples containing references
    t the original objects (i.e. the tuples do not contain deep copies).
    """
    n = len(a)
    p = [i for i in range(n)]          # working array: sorted list of indices
    while True:
        if type(a) == str:
            yield "".join([a[i] for i in p])
        else:
            yield tuple([a[i] for i in p])
        # find the largest j such that p[j] < p[j+1]
        j = n-2
        while j >= 0:
            if p[j] < p[j+1]:  break
            j -= 1
        # exit if p is completely reversed
        if j < 0:
            break
        # find the largest i such that p[j] < p[i]
        i = n-1
        while True:
            if p[j] < p[i]:  break
            i -= 1
        # exchange p[i], p[j]
        p[j], p[i] = p[i], p[j]
        # reverse the items from j+1 to the end of p
        p[j+1:] = reversed(p[j+1:])

# Maps

class Map:
    """
    [TSPLab] A Map is a 2D array of distances between pairs of cities.  Use the index 
    operator to look up the distance between two points.  For example, given a Map object 
    m, call m[a,b] to find the distance between cities a and b.
    """
    
    def __init__(self, arg):
        """
        Create a new Map object.  If the argument is an integer n make a map with n
        cities at random locations (see the method make_random_map for a description of
        how the cities are chosen).  If the argument is a string, read a file with that
        name, either from from the TSPLab data directory (if the name starts with a colon)
        or from the user's current directory.
        """
        self._labels = []
        self._dist = []
        self._coords = []
        self._maxdist = 0
        if type(arg) == str:
            self._read_map_file(arg)
        elif type(arg) == int:
            self._make_random_map(arg)
        else:
            raise TSPError("argument a in Map(a) must be an integer or a file name")
            
    def __repr__(self):
        return "<%s %s>" % (classname(self), str(self._labels))
        
    def __getitem__(self, x):
        """
        Argument x is expected to be an (x,y) pair.  Return the distance between cities
        x and y. 
        """
        a, b = x
        if a not in self._labels or b not in self._labels:  return None
        i = self._labels.index(a)
        j = self._labels.index(b)
        if i < j:
            i, j = j, i
        return self._dist[i][j]
        
    def display(self, fw = None):
        """
        Print the complete set of driving distances in the map in the form of a symmetric
        matrix.  The argument is the field width (number of chars in each matrix entry).  
        If no argument is passed, the method uses the number of letters in the longest 
        city name as the field width.
        """
        if fw == None:
            fw = 1 + max(map(lambda x: len(x) if type(x) == str else len(str(x)), self._labels))
            fw = max(7, fw)
            
        # print header row (city names)
        city = []
        s = ' ' * fw
        fmt = '%' + '%ds' % fw
        for x in self._labels:
            label = fmt % x
            s += label
            city.append(label)
        print(s)
        
        # print rows
        fmt = '%' + '%d.2f' % fw
        for (i, row) in enumerate(self._dist):
            s = city[i]
            for d in row:
                s += fmt % d
            print(s)

    def size(self):
        "Return the number of cities in the map"
        return len(self._labels)
        
    def cities(self):
        "Return a list of city names for this map"
        return list(self._labels)
        
    def coords(self, a):
        "Return a tuple with the map coordinates of city a"
        return self._coords[self._index_of(a)]
        
    def make_tour(self, kind = None, t1 = None, t2 = None, **args):
        """
        Call this method to create a new Tour object with a path that connects cities in this 
        map.  If the 'kind' argument is a list of city names, the tour will include just these cities, 
        in the order they are given (the list does not have to include all the cities).  If 
        the method is called without any arguments it returns a tour that contains all the 
        cities in the order in which they were defined.  Otherwise the first argument should
        be a string and the remaning arguments should be existing Tour objects.
            make_tour()                   make a tour of cities in the order they were defined
            make_tour([x,y,...])          make a tour with cities x, y, ...
            make_tour('random')           make a tour of all cities in a random order
            make_tour('mutate', t1)       return a copy of t1 with a single point mutation
            make_tour('cross', t1, t2)    return a cross between tours t1 and t2.
        """
        if kind == None:
            tour = Tour(self, self._labels)
        elif type(kind) == list:
            tour = Tour(self, kind)
        elif kind == 'random':
            tour = Tour(self, self._labels)
            tour.permute()
        elif kind == 'mutate' and type(t1) == Tour:
            tour = t1.clone()
            tour.mutate(**args)
        elif kind == 'cross' and type(t1) == Tour and type(t2) == Tour:
            tour = t1.clone()
            tour.cross(t2, **args)
        else:
            raise TSPError("make_tour: unknown type: %s %s %s" % (str(kind), str(t1), str(t2)))
        return tour
        
    # A simple 'struct' used in the each_tour generator to associate a flag with each item
    # in the array of indices
    
    class ItemWithDirection:
        def __init__(self, value, direction):
            self.value = value
            self.direction = direction
            
        def __repr__(self):
            arrow = '<' if self.direction else '>'
            return "%s%s" % (arrow, self.value)
            
            
    # Method to generate all (n-1)! / 2 unique tours (avoiding duplicates that are either 
    # rotations or inversions of other tours)
        
    def each_tour(self):
        """
        Generate all possible tours of this map.  Every tour starts in the first city (city 0 
        when city names are integers, or the first city read from the file).  Successive tours 
        are generated by the Johnson-Trotter algorithm, which makes permutations by exchanging 
        just two cities from the previous tour.  The Johnson-Trotter algorithm makes it possible 
        to stop iterating before repeating tours in reverse order.
        """
        # make a list of indices, each associated with the direction it will move; note that
        # index 0 is not in the list
        a = []
        n = len(self._labels)
        for i in range(1,n):
            a.append(Map.ItemWithDirection(i, True))
        # on each iteration exchange two adjacent items in a to make a new permuations
        while True:
            # yield the list of labels appended to label 0 
            yield Tour(self, [self._labels[0]] + [self._labels[x.value] for x in a])
            # find the rightmost movable item
            mover = None
            for i in range(0,len(a)):
                if Map._movable(a, i) and (mover == None or a[i].value > a[mover].value):
                    mover = i
            # if generating all permutations we're done if no movable items
            if mover == None:
                break
            # for TSP: when item 2 has moved to the end and is about to start moving back it
            # means the remaining permutations are inversions of tours already generated
            k = a[mover].value
            if k == 2:
                break
            # exchange the mover with item to left or right, depending on its flag
            if a[mover].direction:
                adj = mover - 1
            else:
                adj = mover + 1
            a[adj], a[mover] = a[mover], a[adj]
            # invert directions
            for i in range(len(a)):
                if a[i].value > k:
                    a[i].direction ^= True 
    
    # Helper function for Johnson-Trotter algorithm

    @staticmethod
    def _movable(a, i):
        if a[i].direction:
            return i > 0 and a[i].value > a[i-1].value
        else:
            return i < len(a)-1 and a[i].value > a[i+1].value

                
    # "private" methods
    
    # Read a list of cities and pairwise distances from a file.  The first part of the
    # file (marked by :map) has coordinates and names of cities.  The second part (marked
    # by :matrix) should have n * (n-1) / 2 lines where each line has the distance between
    # a pair of cities.
    
    def _read_map_file(self, filename):
        section = None
        # if filename[0] == ':':
        #     filename = os.path.join(PythonLabs.datadir, "tsp", filename[1:])
            
        with open(filename) as bodyfile:
            for line in bodyfile:
                line = line.strip()
                if len(line) == 0 or line[0] == '#':  continue
                if line[0] == ':' :
                    if line.startswith(':map'): 
                        section = 'map'
                    elif line.startswith(':matrix'): 
                        section = 'matrix'
                    else:
                        raise TSPError("unknown map descriptor %s " % line)
                    continue
                if section == 'map':
                    try:
                        x, y, name = line.split()
                        self._coords[self._index_of(name)] = (float(x), float(y))
                    except ValueError:
                        print("bad format for map entry: %s" % line)
                elif section == 'matrix':
                    try:
                        a, b, d = line.split()
                        dist = float(d)
                        self._set_distance(a, b, dist)
                        self._maxdist = max(self._maxdist, dist)
                    except ValueError:
                        print("bad format for map distance: %s" % line)
                else:
                    pass    # in case future maps have other sections...
                    
        errs = []
        for (i, row) in enumerate(self._dist):
            for (j, dist) in enumerate(row):
                if dist == None:
                    errs.append((self._labels[i],self._labels[j]))
        if len(errs) > 0:
            raise TSPError("Missing distances: %s" % str(errs))
        
    # Return the index of city a, extending the city list and adding a if necessary.
    # When adding a new city, initialize its coordinates and row in the distance matrix.
        
    def _index_of(self, a):
        if a not in self._labels:
            i = len(self._labels)
            self._labels.append(a)
            self._coords.append(None)
            self._dist.append([None]*(i+1))
            self._dist[i][i] = 0
        else:
            i = self._labels.index(a)
        return i
        
    # Save the distance between cities a, b.
    
    def _set_distance(self, a, b, d):
        if a not in self._labels:  
            raise TSPError("unknown city name:  %s" % str(a))
        if b not in self._labels:  
            raise TSPError("unknown city name:  %s" % str(b))
        if a == b:  
            raise TSPError("can't assign to diagonal %s" % str(a))
        i = self._labels.index(a)
        j = self._labels.index(b)
        if i < j:
            i, j = j, i
        self._dist[i][j] = d
    
    # Make a map with n random cities.  To make interesting drawings, there are 400
    # potetntial cities in a 20 x 20 grid.  Draw n at random, and tweak their (x,y)
    # coordinates to move them slightly.  Use our own RandomList class to get n 
    # unique random integers between 0 and 399.
    
    def _make_random_map(self, n):
        self._ids = []
        for (i,city) in enumerate(RandomList(n, 400)):
            x, y = divmod(city, 20)
            x = (20 * x) + randint(0,5) + 50
            y = (20 * y) + randint(0,5) + 50
            self._coords[self._index_of(i)] = (x,y)
            self._ids.append(city)
        for i in range(n):
            for j in range(0,i):
                xi, yi = self._coords[i]
                xj, yj = self._coords[j]
                d = sqrt((xi - xj)**2 + (yi - yj)**2)
                self._dist[i][j] = d
                self._maxdist = max(self._maxdist, d)
    
# Tours

class Tour:
    """
    [TSPLab] A Tour object is an array of city names, corresponding to the cities visited, 
    in order, by the salesman.  Attributes are the path, its cost, a unique tour ID, and 
    a reference to the map used to define the distance between pairs of cities.

    Class methods access the number of tours created or reset the tour counter to 0.  There
    is a constructor, but users should call the make_tour method of the Map class to
    create a new tour instead of calling Tour() directly.
    """
    
    _count = 0                         # class variable to keep track of the number of tours
    
    @staticmethod
    def count():
        "Return the number of Tour objects created."
        return Tour._count
        
    @staticmethod
    def reset():
        "Set the tour counter back to 0."
        Tour._count = 0
    
    def __init__(self, m, a):
        """
        Create a new tour using costs defined by Map object m.  The array a should be
        a list of cities in m.  The TSP algorithm does not call this method directly,
        but instead calls make_tour, a method defined in the Map class.
        """
        if len(a) < 3:
            raise TSPError("tours must have at least 3 cities")
        self._matrix = m
        self._path = copy(a)
        self._cost = self.pathcost()
        self._id = Tour._count
        self._alive = True
        Tour._count += 1
        
    def __repr__(self):
        return "<%s %s %.3f>" % (classname(self), str(self._path), self._cost)
    
    def __lt__(self, rhs):
        "[TSPLab] Compare two tours based on their costs."
        return self._cost < rhs._cost

    def clone(self):
        """
        Make a "deep copy" of this tour object, giving it a copy of the list of cities.
        """
        return Tour(self._matrix, self._path)
        
    def path(self):
        "Return a tuple made from this tour's path."
        return tuple(self._path)
        
    def cost(self):
        "Return this tour's cost"
        return self._cost
        
    def zap(self):
        "Set the 'alive' attribute to False (used by select_survivors)"
        self._alive = False
        
    def alive(self):
        "Return true unless the zap() method was called for this tour"
        return self._alive
        
    def pathcost(self):
        """
        Compute the cost of this tour by summing the distances between cities in the 
        order shown in the current path.  In general users do not need to call this 
        method, since the path is computed when the object is created, and is updated
        automatically by calls to mutate and cross, but this method is used in unit tests 
        to make sure the cost is updated properly by the mutation methods.
        """
        cost = self._matrix[ self._path[0], self._path[-1] ]
        for i in range(len(self._path)-1):
            cost += self._matrix[ self._path[i], self._path[i+1] ]
        return cost
        
    def permute(self):
        """
        Randomly permute the order of cities in this tour (called by make_tour when it
        is creating a new random tour).
        """
        a = self._path
        for i in range(0,len(a)-1):
            r = randint(i, len(a)-1)
            a[i], a[r] = a[r], a[i]
        self._cost = self.pathcost()
            
    # Exchange mutation (called 'EM' by Larranaga et al).  Swaps node i with one
    # d links away (d = 1 means neighbor).  An optimization that has a big impact when
    # tours are 20+ cities computes new cost by subtracting and adding single
    # link costs instead of recomputing full path length.  Notation:  path
    # through node i goes  xi - i - yi, and path through j is  xj - j - yj.
    
    def mutate(self, i = None, distance = None):
        """
        A call of the form t.mutate(i, d) modifies tour t by applying a "point mutation" 
        that swaps the city at location i in the tour with the city d locations away.  If 
        i is None a random location between 0 and n-1 is chosen.  If d is None it is set 
        to 1, i.e. the city at location i is exchanged with the one following it in the tour.
        """
        path = self._path
        n = len(path)
        
        if i == None:
            i = randint(0, n-1)
        if distance == None:  
            distance = 1 
        distance = distance % n
        if distance == 0:     
            return

        j = (i + distance) % n      # will exchange path[i] with path[j]
        
        xi = (i-1) % n              # locations before, after i
        yi = (i+1) % n
        xj = (j-1) % n              # locations before, after j
        yj = (j+1) % n
        
        if distance == 1:
            self._cost -= self._matrix[ path[xi], path[i] ]
            self._cost -= self._matrix[ path[j], path[yj] ]
            self._cost += self._matrix[ path[xi], path[j] ]
            self._cost += self._matrix[ path[i], path[yj] ]
        else:
            self._cost -= self._matrix[ path[xi], path[i] ]
            self._cost -= self._matrix[ path[i], path[yi] ]
            self._cost -= self._matrix[ path[xj], path[j] ]
            self._cost -= self._matrix[ path[j], path[yj] ]
            self._cost += self._matrix[ path[xi], path[j] ]
            self._cost += self._matrix[ path[j], path[yi] ]
            self._cost += self._matrix[ path[xj], path[i] ]
            self._cost += self._matrix[ path[i], path[yj] ]
            
        path[i], path[j] = path[j], path[i]

    def cross(self, other, i = None, size = None):
        """
        A call of the form t.cross(other, i, n) mutates tour t by applying a "cross-over" mutation 
        with another tour.  Arguments i and n specify the starting location and size of the 
        portion of tour t to keep; then cities that are removed are replaced by cities
        in the order in which they appear in the other tour.  If i and n are not specified by the
        caller they are chosen at random.
        """
        path = self._path
        n = len(path)
        
        if i == None:                       # i is the starting index of the segment to keep
            i = randint(0, n-1)
        if size == None:                    # set j to one past the last item to keep
            j = i + randint(2,n//2)
        else:
            j = i + size
        j = j % n
        
        if i < j:                           # keep one contiguous segment
            p = self._path[i:j]
        else:                               # segment wraps around, continues from 0
            p = self._path[i:]
            p += self._path[0:j]
        
        self._path = p
        for city in other._path:
            if city not in self._path:
                self._path.append(city)
        
        self._cost = self.pathcost()

# Exhaustive search

def xsearch(m):
    """
    [TSPLab] Do an exhaustive search of all possible tours of cities in map m,
    returning the tour object that has the lowest cost path.
    """
    best = m.make_tour()
    for t in m.each_tour():
        if t.cost() < best.cost():
            best = t
    return best
    
# Random Search

_rsearch_options = {
    'update' : 10,
    'pause' : 0,
}

def rsearch(m, n, **user_options):
    """
    [TSPLab] Do a random search of the possible tours of cities in map m.  Creates 
    n random tour objects and returns the one that has the lowest cost.  Options
    control how the display is updated when the map is on the canvas:
        update (default 10) is the number of iterations to perform between updates 
        pause (default 0) is the time (in seconds) to pause between updates
    """
    options = dict(_rsearch_options)
    options.update(user_options)
    
    Tour.reset()                        # set tour counter to 0
    
    best = m.make_tour('random')
    if Canvas.view:  
        init_tour_display(best, { 'ntours' : "#tours: 0", 'cost' : "cost:" }, [])
        Canvas.view.options['update'] = options['update']
        Canvas.delay = options['pause']
    
    for i in range(n-1):
        t = m.make_tour('random')
        if t.cost() < best.cost():
            best = t
        if Canvas.view:
            _update_tour_display(t, i)
    
    return best
    
# Genetic algorithm (aka "evolutionary search")
    
_esearch_options = {
    # 'popsize' : 10,
    'profiles' : {
        'mixed'     : (0.5, 0.25, 0.25),
        'random'    : (0.0, 0.0, 0.0),
        'all_small' : (1.0, 0.0, 0.0),
        'all_large' : (0.0, 1.0, 0.0),
        'all_cross' : (0.0, 0.0, 1.0),
    }, 
    'dist' : 'all_small',
    'resume' : False,
    'update' : 1, 
    'pause' : 0.02,
}

previous_population = None
previous_options = None
previous_maxgen = None

def esearch(m, maxgen, popsize, **user_options):
    """
    [TSPLab] Use an evolutionary algorithm to search for the optimal tour of the cities 
    on a map m.  The maxgen argument is the number of cycles of selection and rebuilding 
    to perform.  The return value is the tour object with the lowest cost in the final 
    population.

    The optional arguments specify parameters of the evolutionary algorithm.  Possible 
    options and their defaults are:
        popsize :   10             population size
        dist :      'all_small'    mutation probability distribution (see note below)
        pause :     0.02           time (in seconds) to pause between each generation
        resume :    False          if true resume a previous search
    
    The distribution option is passed to the rebuild_population function to tell it which
    types of mutations to perform when creating new tours.  It can either be a list (or 
    tuple) of three numbers that sum to 1.0 or a string that corresponds to the name of
    a predefined distribution.  The three numbers are the probability of a nearby point
    mutation, a long distance point mutation, or a crossover.  The predefined distributions
    are:
        all_small  : (1.0, 0.0, 0.0)
        all_large  : (0.0, 1.0, 0.0)
        all_cross  : (0.0, 0.0, 1.0)
        mixed      : (0.5, 0.25, 0.25)
    """
    global previous_population, previous_options, previous_maxgen
    
    options = dict(_esearch_options)
    options.update(user_options)
    
    if options['resume']:
        if previous_population:
            population = previous_population
            options = previous_options
            ngen = previous_maxgen
        else:
            raise TSPError("no previous population")
    else:
        _check_mutation_parameters(options)
        Tour.reset()
        # population = init_population(m, popsize = options['popsize'])
        population = init_population(m, popsize)
        ngen = 0
        if Canvas.view:
            Canvas.view.options['update'] = options['update']
            Canvas.delay = options['pause']
    
    dist = options['dist']
    probs = options['profiles'][dist]
    sdmax = 1 if m.size() < 10 else m.size() // 10           # max distance for small point mutation
    ldmax = 1 if m.size() < 10 else m.size() // 4            # and for large point mutation

    evolve(population, m, ngen, maxgen, {'sdmax' : sdmax, 'ldmax' : ldmax, 'probs': probs})

    previous_population = population
    previous_options = options
    previous_maxgen = maxgen
    
    return population[0]
   
# Helper function called from esearch to validate search parameters
 
def _check_mutation_parameters(options):
    dist = options['dist']
    profiles = options['profiles']
    float_error = "distribution must be an array of three numbers between 0.0 and 1.0"
    dist_name_error = "distribution must be one of %s" % [k for k in profiles.keys()]
    if type(dist) == str:
        if options['dist'] not in profiles:
            raise TSPError(dist_name_error)
    elif type(dist) == list or type(dist) == tuple:
        if len(dist) != 3:
            raise TSPError(float_error)
        total = fsum(dist)
        if total != 1.0:
            raise TSPError("sum of probabilities must be 1.0")
        profiles['user'] = dist
        options['dist'] = 'user'
    else:
        raise TSPError(float_error + " or " + dist_name_error)
    
def init_population(m, popsize):
    """
    [TSPLab] Create a list of random tours of the cities in map m.  The popsize
    parameter specifies the number of tours.
    """
    pop = [m.make_tour('random') for i in range(popsize)]
    if Canvas.view:
        init_tour_display(pop[0], { 'ngen' : "generations: 0", 'ntours' : "#tours: 0", 'cost' : "cost:" }, pop)
        Canvas.update()
    return pop
    
def select_with_probability(p):
    return random() < p

def evolve(population, m, gen, maxgen, dist):
    """
    [TSPLab] Main loop of the genetic algorithm to find the optimal tour of a set of 
    cities.  The arguments passed to evolve by esearch (the function called by the user
    to initiate the genetic algorithm) are:
        population:   an array of tour objects created by init_population
        m:            the Map object that specifies cities and distances between cities
        gen:          the current generation number
        maxgen:       stop iterating when gen reaches this number of generations
        dist:         the probability distribution for types of mutations to apply
                      (passed to rebuild_population as it creates new tours)
    """
#     popsize = len(population)
    best = population[0]
    while gen < maxgen:
        # print("sorting...")
        population.sort(key = Tour.cost)
        if Canvas.view:
            _update_histogram(population)
            Canvas.update()
        # print("selecting...")
        select_survivors(population)
        # print("compacting...")
        ns = compact_population(population)
        # print("rebuilding...")
        rebuild_population(population, m, ns, dist)
        if Canvas.view and gen % Canvas.view.options['update'] == 0:
            _update_histogram(population)
            Canvas.update()
        if (population[0].cost() < best.cost()):
            best = population[0]
            if Canvas.view:
                _update_tour_display(best, gen)
                Canvas.update()
        gen += 1
    
    return best
    
def select_survivors(population):
    """
    [TSPLab] Apply "natural selection" to a population (an array of Tour objects).  Sort 
    the array by fitness, then remove individual i with probability i/n where n is the
    population size.  Note the first item in the array is always kept since 0/n = 0.
    """
    n = len(population)
    
    for i in range(1,n):
        if select_with_probability(i/n):
            population[i] = None
            if Canvas.view and i < len(Canvas.view.histogram):  
                Canvas.schedule(SetBarColor(i,'gray'))
    if Canvas.view:
        _update_histogram(population)
        Canvas.update()
    
    
def compact_population(population):
    """
    [TSPLab] Sort the population, moving all Tour objects to the left side and the
    None objects to the right, return the location of the first None.
    """
    d = 0
    for i in range(1,len(population)):
        if population[i] is None:
            d += 1
        elif d > 0:
            population[i-d], population[i] = population[i], population[i-d]
    if Canvas.view:
        _update_histogram(population)
        Canvas.update()
    return len(population) - d
    
def rebuild_population(population, m, ns, dist = {'sdmax' : 1, 'ldmax' : None, 'probs' : (1,0,0)}):
    """
    [TSPLab] Add new tours to a population.  Parameter m is the map (needed to create new Tour
    objects), ns is the number of survivors from the previous generation.  Each new tour is a 
    mutation of one or two survivors.  The dist parameter has information about the type and
    size of mutation to perform.
    """
#     m = Canvas.view.cities
#     
#     psmall, plarge, pcross = dist
#     sdmax = 1 if m.size() < 10 else m.size() / 10           # max distance for small point mutation
#     ldmax = 1 if m.size() < 10 else m.size() / 4            # and for large point mutation
    
#     prev = len(population)
#     while len(population) < n:
    psmall, plarge, pcross = dist['probs']
    for i in range(ns, len(population)):
        r = random()
        if r < 1.0 - pcross:
            mom = population[ randint(0, ns-1) ]
            if r < 1.0 - (plarge + pcross):
                d = randint(1,dist['sdmax'])
            else:
                d = randint(1,dist['ldmax'])
            kid = m.make_tour( 'mutate', mom, distance = d )
        else:
            mom = population[ randint(0, ns-1) ]
            dad = population[ randint(0, ns-1) ]
            kid = m.make_tour( 'cross', mom, dad )
#         population.append(kid)
        population[i] = kid

# Visualization

_map_view_options = {
    'dot_color' : 'lightblue',
    'dot_radius' : 5.0,
}

class MapView:
    def __init__(self, cities, nodes, links, labels, histogram, options):
        self.cities = cities
        self.nodes = nodes
        self.links = links
        self.labels = labels
        self.histogram = histogram
        self.options = options
        self.best = None

def view_map(m, **user_options):
    """
    [TSPLab] Initialize the canvas with a drawing of the cities in map m.  For 
    maps read from a file (e.g. ':ireland.txt') the x and y coordinates of each
    city are specified in the file.  For maps initialized with a call for the 
    form Map(n) there will b cities placed randomly on the canvas.
    
    Options for controlling the color and size of a circle representing a city can
    be passed following m.  The options and their defaults are:
        dot_color  = 'lightblue'
        dot_radius = 5.0
    """
    options = dict(_map_view_options)
    options.update(user_options)
    
    Canvas.init(800, 500, "TSPLab")
    links = []
    nodes = []
    r = options['dot_radius']
    for city in m.cities():
        x, y = m.coords(city)
        nodes.append(Canvas.Circle( x, y, r, fill = options['dot_color'] ))
        Canvas.Text(str(city), x+r, y+r)
    Canvas.register(MapView(m, nodes, links, {}, [], options))

def view_tour(t):
    """
    [TSPLab] Update the drawing on the canvas to show the paths in tour object t.
    A call to view_tour will erase an existing tour and then draw a new set of 
    lines showing the path defined by t.
    """
    if Canvas.view == None:
        raise TSPError("call view_map to initialize the canvas")
    m = Canvas.view.cities
    if m.size() < len(t.path()):
        raise TSPError("call view_map to show the map for this tour")
    Canvas.drawing.delete('path')
    Canvas.view.links = []
    x0, y0 = m.coords(t.path()[-1])
    for i in range(len(t.path())):
        x1, y1 = m.coords(t.path()[i])
        Canvas.view.links.append(Canvas.Line(x0, y0, x1, y1, tag = 'path'))
        x0, y0 = x1, y1
    for x in Canvas.view.nodes:
        Canvas.drawing.lift(x.id)

# Pass one of these events to Canvas.schedule to change the value of a label

class SetLabel:
    "[TSPLab] Update a label on the map display"
    def __init__(self, name, text):
        self.name = name
        self.text = text

    def execute(self, view):
        t = Canvas.view.labels[self.name]
        Canvas.drawing.itemconfigure(t.id, text = self.text)

# Call init_tour_display at the start of esearch or rsearch to initialize the
# labels, draw the first tour, and initialize the histogram of tour costs (which
# will be empty in rsearch, but needs to be erased if rsearch is called after
# esearch).  Also: record the tour as the best seen so far in the Canvas.view.

def init_tour_display(tour, labels, hist):
    view_tour(tour)
    _init_labels(labels)
    _init_histogram(hist)
    Canvas.view.best = tour
    
# Call _update_tour_display in the middle of a search to update the map if a 
# new best tour has been found and to update the text

def _update_tour_display(tour, iteration):
    if tour.cost() < Canvas.view.best.cost():
        view_tour(tour)
        Canvas.schedule(SetLabel('cost', "cost: %.2f" % tour.cost()))
        Canvas.view.best = tour
    if iteration % Canvas.view.options['update'] == 0:
        if 'ntours' in Canvas.view.labels:
            Canvas.schedule(SetLabel('ntours', "#tours: %d" % Tour.count()))
        if 'ngen' in Canvas.view.labels:
            Canvas.schedule(SetLabel('ngen', "#generations: %d" % iteration ))
    if len(Canvas.events) > 0:
        Canvas.update()
    
# Erase any existing labels and draw new ones at the start of a search

_labelx = 525
_labely = 350
_labeldy = 20

_label_map = {              # map label name to row number
    'ngen' : 0,
    'ntours' : 1,
    'cost' : 2
}

def _init_labels(labels):
    for x in Canvas.view.labels.values():
        Canvas.drawing.delete(x.id)
    Canvas.view.labels = { }
    for k in labels:
        dy = _label_map[k] * _labeldy
        Canvas.view.labels[k] = Canvas.Text(labels[k], _labelx, _labely + dy)

# Helper method to draw a histogram of tour costs, called at the start of esearch.
# Note: rsearch calls make_histogram with an empty list to erase any previous histogram
# left by a call to esearch

_hist_x = 520
_hist_y = 100
_hist_ymax = 200
_hist_max_bins = 50
_hist_bin_width = 5

_hist_fill = 'darkblue'

def _init_histogram(pop):
    for x in Canvas.view.histogram:
        Canvas.drawing.delete(x.id)
    Canvas.view.histogram = []
    if len(pop) == 0:
        return
        
    scale = _hist_ymax / pop[-1].cost()             # determine height of tallest bar,
    Canvas.view.options['hscale'] = scale           # save it to use in _update_histogram
    
    pstep = ceil(len(pop) / _hist_max_bins)         # stride for stepping through population
    Canvas.view.options['pstep'] = pstep            # to select costs to draw
    
    nbins = len(pop) / pstep                        # number of boxes to draw
    Canvas.view.options['nbins'] = nbins
    
    # Canvas.view.options['recolor'] = False          # will be set to True when bins need recoloring
    
    x0 = _hist_x
    for i in range(0, len(pop), pstep):
        binsum = 0
        for j in range(i, i+pstep):                 # compute average cost of tours in 
            binsum += pop[j].cost()                 # current bin
        h = (binsum / pstep) * scale
        y0 = _hist_y + _hist_ymax - h
        x1 = x0 + _hist_bin_width
        y1 = _hist_y + _hist_ymax
        Canvas.view.histogram.append(Canvas.Rectangle(x0, y0, x1, y1, fill = _hist_fill))
        x0 += _hist_bin_width
    
def _update_histogram(population):
    scale = Canvas.view.options['hscale']
    pstep = Canvas.view.options['pstep']
    nbins = Canvas.view.options['nbins']
    for (i, box) in enumerate(Canvas.view.histogram):
        binsum = 0
        for j in range(i*pstep, (i+1)*pstep):
            binsum += population[j].cost() if population[j] is not None else 0
        h = (binsum / pstep) * scale
        a = Canvas.drawing.coords(box.id)
        before = a[1]
        a[1] = _hist_y + _hist_ymax - h
        Canvas.drawing.coords(box.id, *a)
        Canvas.drawing.itemconfigure(box.id, fill = _hist_fill)
    
class SetBarColor:
    "[TSPLab] Change the color of histogram bar i"
    def __init__(self, i, color):
        self.index = i
        self.color = color

    def execute(self, view):
        rect = Canvas.view.histogram[self.index]
        Canvas.drawing.itemconfigure(rect.id, fill = self.color)


