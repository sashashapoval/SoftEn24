## Iterative algorithms -- linear search, insertion sort

__all__ = ["Canvas", "Counter", "RandomList", 
    "isearch", "isort", 
    "move_left", "less", "swap", 
    "view_list", "view_list_setup",
    "Touch", "Swap", "SetRegion"]

from .Tools import Counter, RandomList, classname
from .Canvas import Canvas

def isearch(a, x):
    "[IterationLab] Search a for x, returning location or None"
    Counter.reset('comparisons')
    i = 0
    while i < len(a):
        Counter.increment('comparisons')
        if Canvas.drawing:  
            Canvas.schedule(Touch(i)); 
            Canvas.schedule(SetRegion(i+1,len(a))); 
            Canvas.update()
        if a[i] == x: 
            return i
        i += 1
    return None

def isort(a):
    "[IterationLab] Sort items in list a using an insertion sort"
    Counter.reset('comparisons')
    for i in range(1, len(a)):
        if Canvas.drawing:  
            Canvas.schedule(Touch(i)); 
            Canvas.schedule(SetRegion(i+1,len(a))); 
            Canvas.update()
        move_left(a,i)

## Helper functions

def move_left(a, i):
    if Canvas.drawing:
        Canvas.schedule(MoveVertical(i, -1))
        Canvas.update()
    while i > 0 and less(a[i], a[i-1]):
        swap(a,i-1,i)
        i -= 1
    if Canvas.drawing:
        Canvas.schedule(MoveVertical(i, 1))
        Canvas.update()

def less(x, y):
    Counter.increment('comparisons')
    return x < y

def swap(a, i, j):
    a[i], a[j] = a[j], a[i]
    if Canvas.drawing:
        Canvas.schedule(Swap(i,j))
        Canvas.update()
                
## Visualization

# A ListView is a simple struct holding objects and parameters used to construct
# the array sorting visualization

class ListView:
    def __init__(self, array, rects, bar, palette):
        self.array = array
        self.rectangles = rects
        self.bar = bar
        self.palette = palette
        self.amax = max(array)
        self.history = []

# Definition of visualization attributes

_array_fill = 'lightblue'
_bar_fill = '#000080'
_canvas_fill = 'white'
_mark_color = 'blue'

_x0 = 10            # left edge of leftmost bar
_dx = 10            # distance between left edges of adjacent bars
_y0 = 50            # top edege of tallest bar
_y1 = 150           # bottom edge of array bars
_ymin = 3           # minimum height of bar
_dy = 10            # distance to move selected bar up or down

# Compute top edge of a bar as a function of its height relative to the tallest bar

def bar_top(val, amax):
    dy = _y1 - _y0 - _ymin                 # number of pixels to allocate
    return _y1 - _ymin - (val/amax)*dy     # substract percentage from base

# Top level canvas initialization -- make the window, draw a list as a set
# of bars where the height of a bar is proportional to the value at that location.

def view_list(a):
    "[IterationLab] Initialize the PythonLabs Canvas to visualize iterative algorithms"
    Canvas.init(800, 200, "IterationLab: Linear Search, Insertion Sort")
    view_list_setup(a)
    
def view_list_setup(a):
    "[IterationLab] Helper method called by view_list in IterationLab and RecursionLab"
    amax = max(a)
    rects = []
    for (i,n) in enumerate(a):
        rx = _x0 + i*_dx
        ry = bar_top(a[i], amax)
        rects.append(Canvas.Rectangle(rx,ry,rx+_dx,_y1,outline=_canvas_fill,fill=_array_fill))
    progress = Canvas.Rectangle(_x0,_y1+10,_dx*(len(a)+1),_y1+15,outline="white",fill=_bar_fill)
    view = ListView(a, rects, bar=progress, palette=['#000080','#BADFEB'])
    Canvas.register(view)
    return view

## Animation Events

class Touch:
    "[IterationLab] Cycle the rectangle for a[i] through a palette of colors"
    def __init__(self, i):
        self.index = i
    
    def execute(self, view):
        rect = view.rectangles[self.index]
        pmax = len(view.palette)
        if len(view.history) >= pmax:  view.history.pop()
        view.history.insert(0,rect)
        for (i,rect) in enumerate(view.history):
            Canvas.drawing.itemconfigure(rect.id, fill = Canvas.view.palette[i])

class Swap:
    "[IterationLab] Exchange the locations of bars i and j"
    def __init__(self, i, j):
        self.i = i
        self.j = j

    def execute(self, view):
        i = min(self.i, self.j)
        j = max(self.i, self.j)
        dist = _dx * (j-i)
        ri = view.rectangles[i]
        rj = view.rectangles[j]
        Canvas.move(ri, dist, 0)
        Canvas.move(rj, -dist, 0)
        view.rectangles[i], view.rectangles[j] = view.rectangles[j], view.rectangles[i]

class MoveVertical:
    def __init__(self, i, dir):
        self.i = i
        self.dir = dir
        
    def execute(self, view):
        ri = view.rectangles[self.i]
        Canvas.move(ri, 0, self.dir * _dy)
        
class SetRegion:
    "[IterationLab] Set the active region bar to be below a[i:j]"
    def __init__(self, i, j):
        self.i = i
        self.j = j

    def execute(self, view): 
        i, j = self.i, self.j
        if i == j:
            Canvas.drawing.itemconfigure(view.bar.id, fill = _canvas_fill)
        else:
            Canvas.drawing.itemconfigure(view.bar.id, fill = _bar_fill)
            if j < i: i, j = j, i
            i = max(i,0)
            j = min(j,len(Canvas.view.array))
            c = Canvas.drawing.coords(view.bar.id)
            c[0] = _x0 + i*_dx
            c[2] = _x0 + j*_dx
            Canvas.drawing.coords(view.bar.id, *c)

