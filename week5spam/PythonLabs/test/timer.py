import sys
from itertools import repeat
from random import randint

app, size, iter = sys.argv

size = int(size)
iter = int(iter)

a = list(repeat(None, size))

for i in range(iter):
    x = randint(0,size-1)
    a[x] = x
    
