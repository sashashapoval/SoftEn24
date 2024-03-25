# Hash table project

# __all__ = ["HashTable", "RandomList"]

from .Tools import RandomList

## Hash functions

# Hash functions computed using the radix-128 values of a string:
#   h0 -- the first character
#   h1 -- first two charcters
#   hn -- all characters
# An optional second argument is a table size n; if present (and not 0)
# return the radix-128 value mod n.

def h0(s, n = None):
    "[HashLab] Compute the hash value of string s, using only the first letter"
    if n:
        return ord(s[0]) % n
    else:
        return ord(s[0])

def h1(s, n = None):
    "[HashLab] Compute the hash value of string s, using the first two letters"
    if n:
        return char_product(2,s) % n    # char_product succeeds if s has only one char
    else:
        return char_product(2,s)

def hn(s, n = None):
    "[HashLab] Compute the radix-128 value of string s"
    if n:
        return char_product(len(s), s) % n
    else:
        return char_product(len(s), s)

# helper function -- compute product of ASCII values of first n chars of s

def char_product(n,s):
    res = 0
    for ch in s[0:n] :
        res = res * 128 + ord(ch)
    return res

## Standalone table insert and lookup functions

# Preliminary versions of insert and lookup, using function h0 and tables
# with exactly 128 rows.

def insert(s, t):
    if (len(t) != 128):
        raise IndexError("table must have 128 rows")
    i = h0(s)
    print(i)
    if t[i] == None:
        t[i] = s
        return i
    else:
        return None

def lookup(s, t):
    if (len(t) != 128):
        raise IndexError("table must have 128 rows")
    i = h0(s)
    if t[i] == s:
        return i
    else:
        return None
    
## Print tables

def print_table(t):
    for (i,row) in enumerate(t):
        if row:
            print("%3d: %s" % (i,str(row)))
