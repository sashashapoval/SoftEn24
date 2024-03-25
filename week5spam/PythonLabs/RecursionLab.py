# Divide and conquer algorithms -- binary search, merge sort, quicksort

__all__ = ["Counter", "Canvas", "RandomList", 
    "bsearch", "msort", "qsort", "isort", "partition",
    "less", "merge_groups", "print_bsearch_brackets", "print_msort_brackets",
    "demo_list", "view_list", 
    "Touch", "Swap", "SetRegion", "Mark", "StartGroup", "MoveUp", "MoveDown"]

from .Tools import Counter, RandomList, classname
from .IterationLab import Touch, Swap, SetRegion, isort, less, view_list_setup
from .Canvas import Canvas

def bsearch(a, target):
    "[RecursionLab] Use a binary search to find target in list a"
    lower = -1
    upper = len(a)
    Counter.reset('comparisons')
    if Canvas.drawing:
        for rect in Canvas.view.history:
            Canvas.drawing.itemconfigure(rect.id, fill = '#BADFEB')
        Canvas.view.history = []
    while upper > lower + 1:
        mid = (lower + upper) // 2
        if Canvas.drawing:
            Canvas.schedule(Touch(mid))
            Canvas.schedule(SetRegion(lower+1,upper))
            Canvas.update()
#         print_bsearch_brackets(a,lower,mid,upper)
        Counter.increment('comparisons')
        if upper == lower + 1: 
            return None
        if a[mid] == target:
            return mid
        if target < a[mid]:
            upper = mid
        else:
            lower = mid
    return None
    
def msort(a):
    "[RecursionLab] Sort list a using the merge sort algorithm"
    Counter.reset('comparisons')
    size = 1
    while size < len(a):
        # print_msort_brackets(a, size)
        merge_groups(a, size)
        size *= 2

def qsort(a, p = None, r = None):
    "[RecursionLab] Sort list a using the quicksort algorithm"
    if p == None:  p = 0; r = len(a)-1;  Counter.reset('comparisons')
    if p < r:
        q = partition(a, p, r)
        qsort(a, p, q-1)
        qsort(a, q+1, r)
        if Canvas.drawing:
            Canvas.schedule(Mark(q, '#BADFEB'))
            Canvas.update()

def partition(a, p, r):
    x = a[p]
    i = p
    if Canvas.drawing:
        Canvas.schedule(Mark(i,'darkgreen'))
        Canvas.update()
    for j in range(p+1, r+1):
        if Canvas.drawing:  Canvas.schedule(Touch(j))
        if a[j] <= x:
            i += 1
            a[i], a[j] = a[j], a[i]
            if Canvas.drawing:
                Canvas.schedule(Touch(i))
                Canvas.schedule(Swap(i,j))
        if Canvas.drawing:  Canvas.update()
    a[p], a[i] = a[i], a[p]
    if Canvas.drawing:
        Canvas.schedule(Swap(p,i))
        Canvas.update()
    return i

## Helper Functions

# In merge_groups:  On each iteration of the while loop i points to the start of 
# the first group, j points to the start of the second group (which is also the 
# end of the first group), k points to the end of the second group
 
# from heapq import merge

def merge_groups(a, gs):
    "[RecursionLab] Merge all pairs of adjacent groups of size gs in a"
    i = 0
    while i < len(a):
        j = i + gs if i + gs < len(a) else len(a)
        k = j + gs if j + gs < len(a) else len(a)
        a[i:k] = merge(a,i,j,k)
        i += 2*gs

# Notation:
#   i, j are indices into group 1, 2
#   ix, jx are indices of ends of groups

def merge(a,i,j,jx):
    ix = j
    res = []
    if Canvas.drawing:  
        Canvas.schedule(StartGroup(i))
        Canvas.schedule(SetRegion(i,jx))
    while i < ix or j < jx:
        if j == jx or i < ix and less(a[i],a[j]):
            if Canvas.drawing:  Canvas.schedule(Touch(i)); Canvas.update(); Canvas.schedule(MoveDown(i,len(res))); Canvas.update()
            res.append(a[i])
            i += 1
        else:
            if Canvas.drawing:  Canvas.schedule(Touch(j)); Canvas.update(); Canvas.schedule(MoveDown(j,len(res))); Canvas.update()
            res.append(a[j])
            j += 1
        # if Canvas.drawing:  Canvas.update()
    if Canvas.drawing:
        Canvas.schedule(MoveUp())
        Canvas.update()
    return res

def print_msort_brackets(a,gs):
    "[RecursionLab] Print the list a with square brackets around groups of size gs"
    res = []
    i = 0
    while i < len(a):
        j = i + gs if i + gs < len(a) else len(a)
        res.append(" ".join(map(str,a[i:j])))
        i += gs
    print("[" + "] [".join(map(str,res)) + "]")
    
def print_bsearch_brackets(a, left, mid, right):
    segs = list(map(lambda s: (' ' + str(s) + ' '), a))
    if right > left + 1:
        segs[left+1] = '[' + segs[left+1][1:]
        segs[right-1] = segs[right-1][:-1] + ']'
        if right > left + 2:
            segs[mid] = '*' + segs[mid][1:]
    elif left == -1:
        segs[0] = '[]' + segs[0][1:]
    elif right == len(a):
        segs[-1] = segs[-1][:-1] + '[]'
    else:
        segs[left+1] = ']' + segs[left+1][1:]
        segs[right-1] = segs[right-1][:-1] + '['
    print(''.join(segs))

## Visualization

# Make an instance of the list from Fig 5.3 so students can visualize various searches

def demo_list():
    return [2,10,17,21,29,46,50,67,69,70,79,83,87,91,94]

# Create the canvas (sized for merge sort), call the setup method in IterationLab to
# create the graphic objects and save the ListView structure, then define the full
# palette to use in viewing binary search.

_tdy = 150              # vertical space between array and temp area

def view_list(a):
    "[RecursionLab] Initialize the PythonLabs Canvas to visualize divide and conquer algorithms"
    if len(a) < 2:
        raise IndexError("visualization defined for arrays of 2 or more items")
    Canvas.init(800, 400, "RecursionLab: Binary Search, Merge Sort, Quicksort")
    view_list_setup(a)
    Canvas.view.palette = Canvas.palette((0,0,128),(182,224,234),4)
    Canvas.view.palette[-1] = '#BADFEB'
    c0 = Canvas.drawing.coords(Canvas.view.rectangles[0].id)
    c1 = Canvas.drawing.coords(Canvas.view.rectangles[1].id)
    Canvas.view.tx = c0[0]          # initial left x of temp area
    Canvas.view.dx = c1[0] - c0[0]  # horizontal space between rectangles

class Mark:
    "[RecursionLab] Change the color of bar i"
    def __init__(self, i, color):
        self.index = i
        self.color = color

    def execute(self, view):
        rect = view.rectangles[self.index]
        Canvas.drawing.itemconfigure(rect.id, fill = self.color)

class StartGroup:
    "[RecursionLab] Record the beginning location of a pair of groups"
    def __init__(self, i):
        self.start = i

    def execute(self, view):
        Canvas.view.groupstart = self.start
        Canvas.view.group = []

class MoveDown:
    "[RecursionLab] Move bar i to location j in the temp area"
    def __init__(self, i, j):
        self.i = i
        self.j = j

    def execute(self, view):
        rect = view.rectangles[self.i]
        coords = Canvas.drawing.coords(rect.id)
        oldx = coords[0]
        newx = Canvas.view.tx + (Canvas.view.groupstart + self.j) * Canvas.view.dx
        Canvas.drawing.move(rect.id, newx - oldx, _tdy)
        Canvas.view.group.append(rect)

class MoveUp:
    "[RecursionLab] Move all the rectangles in the temp area back to the main array area"
    def __init__(self):
        pass
        
    def execute(self, view):
        for r in Canvas.view.group:
            Canvas.drawing.move(r.id, 0, -_tdy)
        ri = Canvas.view.groupstart
        rj = ri + len(Canvas.view.group)
        Canvas.view.rectangles[ri:rj] = Canvas.view.group
