# Classic Sieve of Eratosthenes implemented in Python

__all__ = ["sieve", "view_sieve", "mark_multiples", "erase_multiples", "Canvas"]

from math import sqrt, ceil

_sieve_options = {
    'vis' : False,
    'delay' : 0.5,
}

def sieve(n, **user_options):
    "[SieveLab] Sieve of Eratosthenes (with optional visualization)"
    options = dict(_sieve_options)
    options.update(user_options)
    worksheet = [None, None] + list(range(2,n))
    if options['vis']:
        view_sieve(worksheet, **options) 
        Canvas.delay = options['delay']     
    limit = ceil(sqrt(n))
    for i in range(2,limit):
        if worksheet[i]:
            for j in range(i**2, n, i):
                worksheet[j] = None
            if options['vis']:
                mark_multiples(i,worksheet)
                erase_multiples(i,worksheet)
    return list(filter((lambda x: x), worksheet))
    
# helper function, not used by top level, but available for interactive experiments

# def sift(k, a):
#     "[SieveLab] Remove multiples of k from list a, starting with k**2"
#     for i in range(k**2, len(a), k):
#         a[i] = None    

## Visualization

from .Canvas import Canvas

class SieveView:
    def __init__(self, a, options):
        self.array = a
        self.options = options

_ax = 25        # coordinates of upper left cell
_ay = 25
_cx = 30        # x, y, dimensions of one array cell
_cy = 20
_dx = 5         # distance between adjacent cells
_dy = 5

_sieve_view_options = {
    'nrows' : 10,
    'ncols' : 10,
}

def view_sieve(a, **user_options):
    "[SieveLab] Display list a in the form of a 2D grid."
    options = dict(_sieve_view_options)
    options.update(user_options)
    nrows = options['nrows']
    ncols = options['ncols']
    width = _ax * 3 + ncols * (_cx + _dx)
    height = _ay * 3 + nrows * (_cy + _dy)
    Canvas.init(width, height, "SieveLab")
    for i, val in enumerate(a):
        row = i // ncols
        col = i % ncols
        x = _ax + col * (_cx + _dx)
        y = _ax + row * (_cy + _dy)
        draw_cell(i, val, x, y)
    view = SieveView(a, options)
    Canvas.register(view)
    Canvas.delay = 0
    return view
    
def mark_multiples(n, a):
    "[SieveLab] Circle a[n] to show it's prime and gray out multiples of a[n]."
    if Canvas.drawing:
        Canvas.schedule(Highlight(n))
        for i in range(n*2, len(a), n):
            Canvas.schedule(Mark(i))
        Canvas.update()
    
def erase_multiples(n, a):
    "[SieveLab] Clear the grayed out cells on the canvas to get ready for the next round."
    if Canvas.drawing:
        for i in range(n*2, len(a), n):
            a[i] = None
            Canvas.schedule(Erase(i))
        Canvas.update()

def draw_cell(loc, label, x, y):
    Canvas.Rectangle(x, y, x+_cx, y+_cy, fill = 'white', outline = 'white', tag = 'r' + str(loc))
    if label == None:
        s = ''
    else:
        s = str(label)
    Canvas.Text(s, x + _cx/2, y + _cy/2, anchor = 'center', tag = 't' + str(loc))
    
class Highlight:
    "[SieveLab] Highlight a number"
    def __init__(self, n):
        self.n = n

    def execute(self, view):
        Canvas.drawing.itemconfigure('r' + str(self.n), outline = 'blue')

class Mark:
    "[SieveLab] Highlight a number"
    def __init__(self, n):
        self.n = n

    def execute(self, view):
        Canvas.drawing.itemconfigure('r' + str(self.n), fill = 'lightgray')

class Erase:
    "[SieveLab] Erase a cell"
    def __init__(self, n):
        self.n = n

    def execute(self, view):
        Canvas.drawing.dchars('t' + str(self.n), 0, 'end')
        Canvas.drawing.itemconfigure('r' + str(self.n), fill = 'white')


