## Codes, Text Compression, Error Detection

__all__ = ["Code", "Hex", # "Message", 
    "Node", "PriorityQueue", "Canvas", "Zero", "One", "log2", "path_to_data",
    "encode", "decode", "garbled",
    "read_frequencies", "init_queue", "build_tree", "read_test_data",
    "make_codes", "print_codes", "assign_codes", "huffman_encode", "huffman_decode",
    "view_queue", "erase_node", 
    "tree_sep",
    "RandomList"]

import PythonLabs
from .Tools import RandomList, PQBase, classname, log2, prefix, path_to_data
from .Canvas import Canvas
import os
import sys
from random import randint
from copy import deepcopy

## Code

# Objects of the Code class are sequences of binary digits.  They implement many
# (but not all) of the mutable sequence operations.

from math import ceil

class Code:
    """
    [BitLab] A Code object is the binary representation of an integer or character.  Codes have
    many of the same operations as mutable sequences:  access or modify individual bits, or append
    additional bits.  Note: bits are numbered with bit 0 on the
    left, e.g. if x is the code 1000 then x[0] is 1 and x[3] is 0.
    """
    def __init__(self, x, length=None):
        """
        [BitLab] Create a new binary code object representing the value of x (an integer or a 
        character).  If the second argument is supplied it is used as the length of the code,
        padding with leading 0s or ignoring higher order bits as necessary.
        """
        if type(x) == str:
            if len(x) > 1: raise TypeError("single character only")
            if ord(x[0]) > 127:  raise TypeError("ASCII characters only")
            self._value = ord(x[0])
            self._length = 7
        else:
            if length == None:  
                length = ceil(log2(x+1))
                length = max(length,1)
            self._value = x % (1 << length)
            self._length = length
        self._has_parity_bit = False
        self._base = 2
        
    # Representations -- __repr__ creates a string of digits, __str__ does type conversion
    # to a character (would be nice if we could overload chr, but...)
        
    _digits = "0123456789ABCDEF"
        
    def __repr__(self):
        "[BitLab] Generate the string of digits in the representation of this code"
        if self._length == 0:
            return ""
        else:
            digits = []
            n = self._value
            for i in range(self._length):
                n, d = divmod(n, self._base)
                digits.insert(0, Code._digits[d])
            return "".join(digits)
            
    # def __str__(self):
    #     "[BitLab] Return a one-letter string with the character encoded by this code"
    #     # note: derived class doesn't have parity_bit attribute, so don't check it
    #     if self._value < 128:
    #         if type(self) == Code and self._has_parity_bit:
    #             if self.even_parity():
    #                 return chr(self._value >> 1)
    #             else:
    #                 return '\u2022'     # bullet ( ° )
    #         else:
    #             return chr(self._value)
    #     else:
    #         raise ValueError("conversion to string only for ASCII codes")

    # Operators
    
    def __int__(self):
        return self._value
    
    def __len__(self):
        "[BitLab] Return the length (in bits) of this binary code"
        return self._length
    
    def _slicebounds(self, x):
        "[BitLab] Helper function for __getitem__ and __setitem__"
        if type(x) == slice:
            i = x.start
            j = x.stop
        else:
            i = x
            j = x + 1
        if i >= self._length or j > self._length:  raise IndexError("Code slice requires i <= j < length")
        return (i,j)
    
    def __getitem__(self, x):
        "[BitLab] Return a new Code object made from bit i or bits i:j of this binary code"
        i, j = self._slicebounds(x)
        if i >= j: return Code(0,0)
        mask = (1 << (j-i)) - 1
        val = self._value >> (self._length - j) & mask
        return Code(val,j-i)
        
    def __setitem__(self, x, n):
        "[BitLab] Set bit i or bits i:j of this binary code to the binary value of integer n"
        i, j = self._slicebounds(x)
        if i >= j: return
        mask = (1 << (j-i)) - 1
        n &= mask
        self._value &= ~(mask << (self._length - j))
        self._value |= (n << (self._length - j))
        
    def __lt__(self, x):
        return self._value < x._value
        
    def __le__(self, x):
        return self._value <= x._value

    def __eq__(self, x):
        return self._value == x._value

    def __ne__(self, x):
        return self._value != x._value

    def __gt__(self, x):
        return self._value > x._value

    def __ge__(self, x):
        return self._value >= x._value
    
    # Boolean operatorsBoth + and | are inclusive OR, * and & are AND,
    # and ^ is exclusive OR.
    
    def __invert__(self):
        "[BitLab] Logical negation of this code"
        # constructor 
        return Code(~self._value & sys.maxsize, self._length)

    def __or__(self, x):
        "[BitLab] Logical OR of self and x (LSB only)"
        n = max(self._length, x._length)
        return Code(self._value | x._value, n)
                
    def __and__(self, x):
        "[BitLab] Logical AND of self and x (LSB only)"
        n = max(self._length, x._length)
        return Code(self._value & x._value, n)

    def __xor__(self, x):
        "[BitLab] Exclusive OR of self and x (LSB only)"
        n = max(self._length, x._length)
        return Code(self._value ^ x._value, n)

    # The addition operators perform concatenation (as in strings and lists)
    
    def __add__(self, x):
        "[BitLab] Concatenate this code with the bits in x"
        if type(x) == Code:
            other = x
        elif x is 0:
            other = Zero
        elif x is 1:
            other = One
        else: 
            raise TypeError("argument to extend must be an int or another code")
        val = (self._value << other._length) | other._value
        return Code(val, self._length + other._length)
        
    def __iadd__(self, x):
        "[BitLab] Extend this code by appending the bits in x"
        self.extend(x)
        return self

    # Other methods
        
#     def value(self):
#         "[BitLab] Return the numeric value of this binary code"
#         return self._value
        
    # def append(self, x):
    #     "[BitLab] Add the single bit x to the end of this code"
    #     self._value = (self._value << 1) | (x & 1)
    #     self._length += 1
    #     return self
        
    def extend(self, x):
        "[BitLab] Extend this code by appending the bits in x"
        if type(x) == Code:
            other = x
        elif x is 0:
            other = Zero
        elif x is 1:
            other = One
        else: 
            raise TypeError("argument to extend must be an int or another code")
        self._value = (self._value << other._length) | other._value
        self._length += other._length
        
    def parity_bit(self):
        "[BitLab] Compute the bit that needs to be added to this code to give it even parity"
        x = self._value
        masksize = ceil(log2(sys.maxsize)/2)
        while masksize > 0:
            # print(masksize, Code(x))
            x = (x >> masksize) ^ (x & 2**masksize-1)
            masksize >>= 1
        return x
    
    def add_parity_bit(self):
        "[BitLab] Attach a bit to this binary code, resulting in a code that has even parity"
        if not self._has_parity_bit:
            self.extend(self.parity_bit())
            self._has_parity_bit = True
        
    def even_parity(self):
        "[BitLab] Return True if this binary code has even parity"
        return self.parity_bit() == 0
        
    def flip(self, i):
        "[BitLab] Invert bit i of this binary code"
        self._value ^= (1 << self._length - i - 1)
        
    def char(self):
        "[BitLab] Return a one-letter string with the character encoded by this code"
        if self._has_parity_bit and self._value < 256:
            if self.even_parity():
                return chr(self._value >> 1)
            else:
                return '\u2022'     # bullet ( ° )
        elif self._value < 128:
            return chr(self._value)
        else:
            raise ValueError("conversion to string only for ASCII codes")
            
# Global constants exported by module

Zero = Code(0)
One = Code(1)
        
class Hex(Code):
    "[BitLab] Call Hex(n) to get an object that represents the hexadecimal encoding of an integer n."
    def __init__(self, x, length=None):
        if type(x) == str:
            if len(x) > 1: raise TypeError("codes represent a single character only")
            self._value = ord(x[0])
            self._length = 2
        else:
            if length == None:
                nbits = ceil(log2(x+1))
                length = (nbits + 3) // 4
                length = max(length,1)
            self._value = x % (1 << 4*length)
            self._length = length
        self._base = 16
    
    def __getitem__(self, x):
        "[BitLab] Return a new Hex object made from digit i or digits i:j of this hex code"
        i, j = self._slicebounds(x)
        if i >= j: return None
        mask = (1 << 4*(j-i)) - 1
        val = self._value >> 4*(self._length - j) & mask
        return Hex(val,j-i)

    def __setitem__(self, x, n):
        "[BitLab] Set digit i or digits i:j of this hex code to the value of integer n"
        i, j = self._slicebounds(x)
        if i >= j: return
        mask = (1 << 4*(j-i)) - 1
        n &= mask
        self._value &= ~(mask << 4*(self._length - j))
        self._value |= (n << 4*(self._length - j))

    # def append(self, x):
    #     "[BitLab] Append a digit corresponding to the value of x to the end of this hex code"
    #     self._value = (self._value << 4) | (x & 0xF)
    #     self._length += 1
    #     return self

    def extend(self, x):
        "[BitLab] Append the digits in hex code x to the end of this hex code"
        if type(x) != Hex:  raise TypeError("Hex can only be extended by another Hex")
        self._value = (self._value << 4 * x._length) | x._value
        self._length += x._length
        return self

    def parity_bit(self):
        "[BitLab] Undefined for hex codes (raises a NotImplementedError)"
        raise NotImplementedError("parity_bit not defined for Hex codes")
        
    def add_parity_bit(self):
        "[BitLab] Undefined for hex codes (raises a NotImplementedError)"
        raise NotImplementedError("add_parity_bit not defined for Hex codes")
    
    def even_parity(self):
        "[BitLab] Undefined for hex codes (raises a NotImplementedError)"
        raise NotImplementedError("even_parity not defined for Hex codes")

    def flip(self, i):
        "[BitLab] Undefined for hex codes (raises a NotImplementedError)"
        raise NotImplementedError("flip not defined for Hex codes")
        
    def char(self):
        if self._value < 128:
            return chr(self._value)
        else:
            raise ValueError("conversion to string only for ASCII codes")

## Encoding and decoding functions

def encode(s, with_parity = False):
    """
    [BitLab] Create a list of Code objects for the characters in string s.  All characters
    must be in the ASCII character set, and Codes will all have 7 digits.
    """
    res = []
    for ch in s:
        if ord(ch) > 127:
            raise ValueError("characters must be ASCII")
        c = Code(ord(ch),7)
        if with_parity:
            c.add_parity_bit()
        res.append(c)
    return res
    
def decode(m):
    """
    [BitLab] Convert a list of Code objects into a string of characters.
    """
    if type(m) == list:
        return "".join([x.char() for x in m])
    elif type(m) == Code:
        return m.char()
    else:
        raise ValueError('expecting a single Code object or a list of Codes')

def garbled(msg, n):
    "[BitLab] Return a copy of message m with n random 1-bit errors."
    if not msg[0]._has_parity_bit:
        raise ValueError('expecting a list of codes with parity bits')
    nbits = sum(list(map(len,msg)))
    if n >= nbits:
        raise ValueError('too many errors')
    locs = set()
    while len(locs) < n:
        locs.add(randint(0,nbits-1))
    msg = deepcopy(msg)
    for i in locs:
        x, y = divmod(i, len(msg[0]))
        msg[x].flip(y)
    return msg
    
## Utility functions

def make_codes(seq):
    "[BitLab] Create a dictionary that maps each item in a sequence to a unique binary code."
    n = ceil(log2(len(seq)))        # number of bits required for code
    codes = {}
    for (i,x) in enumerate(seq):
        codes[x] = Code(i,n)
    return codes

def print_codes(d, mode = 'by_code'):
    """
    [BitLab] Print the codes produced by a call to make_codes.  The mode argument can be
    'by_code' or 'by_name' and determines how the output is ordered.
    """
    if mode == 'by_code':
        pairs = [(code,name) for (name, code) in d.items()]
    elif mode == 'by_name':
        pairs = [(name,code) for (name, code) in d.items()]
    else:
        raise NotImplementedError("mode must be 'by_code' or 'by_name'")
    pairs.sort(key = lambda x: x[0])
    for x in pairs:
        print(x[0], ': ', x[1])

## Message

# class Message:
#     
#     def __init__(self, packed = False):
#         "[BitLab] Create a new message, initially with 0 bits"
#         self._packed = packed
#         if packed:
#             self._list = [ Code(0,0) ]
#         else:
#             self._list = [ ]
#             
#     def __repr__(self):
#         "[BitLab] Print a message as a string of 0s and 1s"
#         if self._packed:
#             return "".join(map(str,self._list))
#         else:
#             return " ".join(map(str,self._list))
#             
#     def __len__(self):
#         "[BitLab] Return the length (in bits) of a message"
#         return sum(map(len,self._list))
#         
#     def __getitem__(self, x):
#         "[BitLab] Access individual bytes in a message"
#         return self._list[x]
# 
#     def list(self):
#         "[BitLab] Return the list of bytes in the message"
#         return self._list
#     
#     _packsize = 8                   # number of bits per "word" in packed messages
#     
#     def packed(self):
#         "[BitLab] Return True if this message uses a packed format"
#         return self._packed
#         
#     def copy(self):
#         "[BitLab] Return a deep copy of this message"
#         return deepcopy(self)
#         
#     def extend(self, code):
#         "[BitLab] Attach a code to the end of this message"
#         if self._packed:
#             if len(self._list[-1]) + len(code) <= Message._packsize:
#                 self._list[-1].extend(code)
#             else:
#                 n = Message._packsize - len(self._list[-1])
#                 m = len(code) - n
#                 self._list[-1].extend(code[0:n])
#                 self._list.append(code[n:len(code)])
#         else:
#             self._list.append(code)
#         return self


## Priority Queue for BitLab.  Adds visualization calls to the insert and pop methods.

class PriorityQueue(PQBase):
    """
    [BitLab] A PriorityQueue is an ordered collection of items.  Add items by calling
    insert, remove the first item by calling pop.
    """
    def __init__(self):
        "[BitLab] Create a new priority queue, initially empty."
        super().__init__()
        self._on_canvas = False
        
    def insert(self, x):
        "[BitLab] Insert item x into this queue, maintaining items in sorted order"
        res = super().insert(x)
        if self._on_canvas:  move_tree_in(self, x)
#         return res

    def pop(self):
        "[BitLab] Remove the first item from this queue (the item is returned as the value of the call)"
        res = super().pop()
        # if self._on_canvas:  move_tree_down(res)
        if self._on_canvas:  Canvas.schedule(MoveDown(res)); Canvas.update()
        return res

## Utilities for Huffman tree projects

def read_frequencies(filename):
    """
    [BitLab] Read a set of letter frequencies from a file.  Each line should start with a single
    character followed by white space and the frequency of the letter (a number between 0 and 1). 
    """
    a = { }
    # if filename[0] == ':':
    #     filename = os.path.join(PythonLabs.datadir, "huffman", filename[1:])
    with open(filename) as freqfile:
        for line in freqfile:
            if line[0] == '\n' or line[0] == '#':  continue
            letter, freq = line.split()
            a[letter] = float(freq)
    return a

def init_queue(a):
    """
    [BitLab] A convenience function to create a new priority queue and initialize it with a
    Node object for every entry in dictionary a (compatible with the dictionary returned by
    a call to read_frequencies).
    """
    p = PriorityQueue()
    for x in a:
        p.insert(Node(x, a[x]))
    return p
    
def build_tree(filename):
    """
    [BitLab] Create a Huffman tree using freq (a dictionary mapping letters to frequencies).
    """
    pq = init_queue(read_frequencies(filename))
    while len(pq) > 1:
        n1 = pq.pop()
        n2 = pq.pop()
        pq.insert(Node(n1,n2))
    return pq[0]
    
def assign_codes(tree, code = { }, prefix = Code(0,0)):
    """
    [BitLab] Traverse a Huffman tree to create labels for each leaf node.  Return a dictionary
    that maps letters to their variable-length binary codes.
    """
    if tree._char:
        code[tree._char] = prefix
    else:
        assign_codes(tree._left, code, prefix + 0)
        assign_codes(tree._right, code, prefix + 1)
    return code
    
def huffman_encode(s, tree):
    """
    [BitLab] Return a Code object containing the packed encoding of string s using codes
    defined by a Huffman tree.
    """
    res = Code(0,0)
    bits = assign_codes(tree)
    for ch in s:
        res += bits[ch]
    return res

def huffman_decode(msg, tree):
    """
    [BitLab] Decode msg (a Code object) using codes defined by a Huffman tree.
    """
    res = ""
    path = tree
    for b in msg:
        if path.is_leaf():
            res += path._char
            path = tree
        if b == Zero:
            path = path._left
        else:
            path = path._right
    if path.is_leaf():
        res += path._char
    return res

def read_test_data(source):
    """
    [BitLab] If source is 'words' return a list of Hawaiian words.  If source is 'codes'
    return a set of Code objects created using the Huffman tree for the Hawaiian alphabet.
    """
    if source not in ['words', 'codes']:
        raise ValueError("source must be 'words' or 'codes'") 
    filename = os.path.join(PythonLabs.datadir,'huffman',source+'.txt')
    with open(filename) as datafile:
        data = datafile.readlines()
        if source == 'words':
            return list(map(prefix,data))
        else:
            res = []
            for s in data:
                n = 0
                for ch in s.strip():
                    n = (n << 1) | (ord(ch) & 1)
                res.append(Code(n, len(s)-1))
            return res
    
## Huffman trees

class Node:
    """
    [BitLab] A Node object represents an interior node or a leaf node of a Huffman tree.
    """
    def __init__(self, arg1, arg2):
        """
        [BitLab] Create a new node in a Huffman tree.  If both arguments are existing Node
        objects the new node is an interior node with the existing nodes as left and right
        subtrees.  Otherwise the two arguments should be a letter and a frequency and the
        new node is a leaf for that letter.
        """
        self.id = 'node%d' % (Node._id)
        if type(arg1) == Node and type(arg2) == Node:
            self._left = arg1
            self._right = arg2
            self._char = None
            self._freq = arg1._freq + arg2._freq
            if Canvas.drawing:  self._combine_drawings(arg1, arg2)
        else:
            self._char = arg1
            self._freq = arg2
            self._left = self._right = None
            if Canvas.drawing:  self._init_drawing()
        Node._id += 1
            
    _id = 0

    def __repr__(self):
        "[BitLab] Print a tree as (Char Freq (L) (R))"
        if self.is_leaf():
            return "( %s: %.3f )" % (self._char, self._freq)
        else:
            return "( %.3f %s %s )" % (self._freq, str(self._left), str(self._right)) 

    def __lt__(self, rhs):
        "[BitLab] Compare two nodes based on their frequencies."
        return self._freq < rhs._freq
        
    def is_leaf(self):
        "[BitLab] Return True if this node is a leaf node."
        return self._char is not None
        
    def char(self):
        "[BitLab] Return the character at this node, or None if it is not a leaf."
        return self._char

    def freq(self):
        "[BitLab] Return the frequency at this node."
        return self._freq
        
    def left_child(self):
        "[BitLab] Return the left descendant, or None if the node is a leaf."
        return self._left
        
    def right_child(self):
        "[BitLab] Return the right descendant, or None if the node is a leaf."
        return self._right

    def _init_drawing(self):
        self._lfchain = self._rfchain = self
        self._depth = 0
        self._circle = None
        
    def _combine_drawings(self, left, right):
        draw_root(self, left, right)
        self._depth = 1 + max(left._depth, right._depth)
        self._lfchain = left
        self._rfchain = right
        if left._depth > right._depth:
            right._rfchain = left._rfchain
        elif left._depth < right._depth:
            left._lfchain = right._lfchain
        self._addid(left)
        self._addid(right)
        Canvas.update()
        
    def _addid(self, subtree):
        Canvas.drawing.addtag_withtag(self.id, subtree.id)
        if subtree._left:   self._addid(subtree._left)
        if subtree._right:  self._addid(subtree._right)
            
    def _coords(self):
        [x0, y0, x1, y1] = Canvas.drawing.coords(self._circle.id)
        diam = (x1 - x0) / 2
        return (x0 + diam, y0 + diam)
        
    def _left_edge(self):
        p = self
        x = Canvas.drawing.coords(p._circle.id)[0]
        while p._lfchain != p:
            p = p._lfchain
            xt = Canvas.drawing.coords(p._lfchain.id)[0]
            x = min(x, xt)
        return x
        
    def _right_edge(self):
        p = self
        x = Canvas.drawing.coords(p._circle.id)[2]
        while p._rfchain != p:
            p = p._rfchain
            xt = Canvas.drawing.coords(p._rfchain.id)[2]
            x = max(x, xt)
        return x

## Visualization

class QueueView:
    def __init__(self, queue, options):
        self.queue = queue
        self.options = options

_tree_unit = 24         # pixels per tree "unit" (see drawing algoritm)

_queue_view_options = {
    'width' : 42 * _tree_unit,
    'height' : 17 * _tree_unit,
    'qx' : 50,
    'qy' : 50,
    'nodefill' : "lightblue",
}

def view_queue(pq, **user_options):
    options = dict(_queue_view_options)
    options.update(user_options)
    Canvas.init(options['width'], options['height'], "BitLab: Priority Queue")
    view = QueueView(pq, options)
    Canvas.register(view)
    pq._on_canvas = True
    x = options['qx']
    for node in pq:
        node._init_drawing()
        draw_node(node, x, options['qy'])
        x += 3 * _tree_unit
    return view
    
def draw_node(node, x, y):
    diam = _tree_unit
    circ = Canvas.Circle(x, y, diam/2, fill = _queue_view_options['nodefill'], tag = node.id)
    text = Canvas.Text(node._char, x, y, anchor = 'center', tag = node.id)
    ftext = Canvas.Text("%.2f" % node._freq, x, y-diam, anchor = 'center', font = ("Helvetica", 10), tag = node.id)
    node._circle = circ
    
def draw_root(node, left, right):
    # x = (left._coords.x + right._coords.x) / 2
    # y = left._coords.y + 2 * _tree_unit
    lx, ly = left._coords()
    rx, ry = right._coords()
    x = (lx + rx) / 2
    y = ly - 2 * _tree_unit
    draw_node(node, x, y)
    lseg = Canvas.Line(x, y, lx, ly, tag = node.id)
    rseg = Canvas.Line(x, y, rx, ry, tag = node.id)
    Canvas.drawing.lower(lseg.id)
    Canvas.drawing.lower(rseg.id)

def erase_node(node):
    Canvas.drawing.delete(node.id)
    
class MoveDown:
    "[BitLab] Move a tree node below the queue"
    def __init__(self, node):
        self.node = node

    def execute(self, view):
        Canvas.drawing.move(self.node.id, 0, 4 * _tree_unit)

class MoveTree:
    "[BitLab] Move a tree an arbitrary distance"
    def __init__(self, node, dx, dy):
        self.node = node
        self.dx = dx
        self.dy = dy

    def execute(self, view):
        Canvas.drawing.move(self.node.id, self.dx, self.dy)

def move_tree_in(pq, node):
    i = 0
    dx = Canvas.view.options['qx'] - pq[0]._left_edge()
    while pq[i] != node:
        Canvas.schedule(MoveTree(pq[i], dx, 0)); Canvas.update()
        dx = 3 * _tree_unit - tree_sep(pq[i], node)
        Canvas.schedule(MoveTree(node, dx, 0)); Canvas.update()
        dx = 3 * _tree_unit - tree_sep(pq[i], pq[i+1])
        i += 1
    Canvas.schedule(MoveTree(node, 0, -2 * _tree_unit)); Canvas.update()
    if i < len(pq) - 1:
        dx = 3 * _tree_unit - tree_sep(pq[i], pq[i+1])
        i += 1
        while i < len(pq):
            Canvas.schedule(MoveTree(pq[i], dx, 0))
            i += 1
        Canvas.update()
        
def tree_sep(left, right):
    res = right._coords()[0] - left._coords()[0]
    while left._rfchain != left and right._lfchain != right:
        left = left._rfchain
        right = right._lfchain
        dist = right._coords()[0] - left._coords()[0]
        if dist < res:  res = dist
    return res
    
