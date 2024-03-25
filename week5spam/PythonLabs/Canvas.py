# Functions used to create and manage the PythonLabs Convas

__all__ = ["Canvas", "CanvasError", "tk"]

import sys
if sys.version[0] == '3':
    import tkinter as tk
else:
    import Tkinter as tk        # <- seems to load, but isn't working interactively...

from time import sleep
import math

## Canvas

# The Canvas class has static methods for creating and using a Tk drawing window.
# Subclasses define the sorts of objects used by labs, e.g. make a Canvas.Text object
# to draw a string on the canvas.

# Call Canvas.init(x,y) to create a blank canvas for an interactive project.  Instaniate 
# objects of the subclasses (Canvas.Rectangle, Canvas.Line, etc) to place an object 
# on the canvas."

class Canvas:
    window = None
    drawing = None
    view = None
    events = []
    delay = 0.5
    
    @staticmethod
    def init(canvas_width, canvas_height, title = "PythonLabs"):
        "[PythonLabs] Initialize (or re-initialize) the canvas to the specified width and height."
        padding = 10
        if Canvas.window == None:   
            Canvas.window = tk.Tk()
            Canvas.window['background'] = 'gray'
            Canvas.window.columnconfigure(0, weight=1)
            Canvas.window.rowconfigure(0, weight=1)
            Canvas.drawing = tk.Canvas(Canvas.window, height=canvas_height, width=canvas_width, background='white', highlightthickness=0)
            Canvas.drawing.columnconfigure(0, weight=1)
            Canvas.drawing.rowconfigure(0, weight=1)
            Canvas.drawing.grid(row = 0, column = 0, padx = padding, pady = padding, sticky="nsew")
            Canvas.window.protocol("WM_DELETE_WINDOW", Canvas.close)
        else:
            Canvas.drawing.delete('all')
            Canvas.drawing['width'] = canvas_width
            Canvas.drawing['height'] = canvas_height

        Canvas.window.title(title)
        Canvas.window.geometry('%dx%d+50+50' % (canvas_width + 2*padding, canvas_height + 2*padding))
    
    @staticmethod
    def close():
        "[PythonLabs] Close the canvas window (call Canvas.init again to reopen it)."
        Canvas.window.destroy()
        Canvas.window = None
        Canvas.drawing = None
     
    @staticmethod
    def register(x):
        "[PythonLabs] Save a struct that has all the relevant information about the current drawing."
        if Canvas.window == None:  
            raise CanvasError("call Canvas.init to create the canvas window")
        Canvas.view = x

    @staticmethod
    def height():
        "[PythonLabs] Return the current height (in pixels) of the canvas."
        return Canvas.drawing.winfo_height()
   
    @staticmethod
    def width():
        "[PythonLabs] Return the current width (in pixels) of the canvas."
        return Canvas.drawing.winfo_width()
                
    @staticmethod
    def move(obj, dx, dy, track = False):
        """
        Move obj by dx pixels horizontally and dy pixels vertically.  If track is
        True draw a line from the old position to the new postion (provided the
        object's penpoint attribute has been set).
        """
        if track and obj.penpoint != None: 
            a = Canvas.drawing.coords(obj.id)
            x0 = a[0] + obj.penpoint[0]
            y0 = a[1] + obj.penpoint[1]
            Canvas.drawing.create_line(x0, y0, x0+dx, y0+dy, width=1, fill='#777777')
        Canvas.drawing.move(obj.id, dx, dy)
        Canvas.drawing.lift(obj.id)

    @staticmethod
    def palette(first, last, n):
        "[PythonLabs] Create an array of RGB colors ranging from first to last in n steps"
        d = tuple( ((first[i] - last[i]) // n) for i in range(0,3) )
        res = [first]
        for i in range(0,n):
            prev = res[-1]
            res.append( tuple(prev[i]-d[i] for i in range(0,3)) )
        return ["#%02X%02X%02X" % x for x in res]
    
    @staticmethod
    def schedule(action):
        "[PythonLabs] Add an animation event to the queue"
        Canvas.events.append(action)
        
    @staticmethod
    def update(pause = True):
        "[PythonLabs] Process all the events in the animation queue, then update the canvas and pause"
        while len(Canvas.events) > 0:
            e = Canvas.events.pop(0)
            e.execute(Canvas.view)
        Canvas.window.update()
        if Canvas.delay > 0 and pause:
            sleep(Canvas.delay)
        
    class Text:
        def __init__(self, s, x, y, **options):
            if Canvas.window == None:  
                raise CanvasError("call Canvas.init to create the canvas window")
            params = {'text': s, 'font': ("Helvectica", 12), 'anchor': 'nw'}
            params.update(options)
            self.penpoint = None
            self.text = s
            self.font = ("Helvetica", 11)
            self.id = Canvas.drawing.create_text(x,y, **params)
                        
    class Line:
        def __init__(self, x0, y0, x1, y1, **options):
            if Canvas.window == None:  
                raise CanvasError("call Canvas.init to create the canvas window")
            params = { }
            params.update(options)
            self.penpoint = None
            self.id = Canvas.drawing.create_line(x0, y0, x1, y1, **params)
                    
    class Rectangle:
        def __init__(self, x0, y0, x1, y1, **options):
            if Canvas.window == None:  
                raise CanvasError("call Canvas.init to create the canvas window")
            params = { }
            params.update(options)
            self.penpoint = ((x1-x0)//2, (y1-y0)//2)
            self.id = Canvas.drawing.create_rectangle(x0, y0, x1, y1, **params)
        
    class Circle:
        def __init__(self, x, y, r, **options):
            if Canvas.window == None:  
                raise CanvasError("call Canvas.init to create the canvas window")
            params = { }
            params.update(options)
            self.penpoint = (r, r)
            self.id = Canvas.drawing.create_oval(x-r, y-r, x+r, y+r, **params)
        
    class Polygon:
        def __init__(self, a, **options):
            if Canvas.window == None:  
                raise CanvasError("call Canvas.init to create the canvas window")
            params = { }
            params.update(options)
            self.penpoint = (0,0)
            self.id = Canvas.drawing.create_polygon(a, **params)
            
        def rotate(self, theta):
            """
            Rotate the polygon by an angle theta (expressed in degrees).  The object is
            rotated about the point defined by the first pair of (x,y) coordinates.
            """
            theta = math.radians(theta)
            a = Canvas.drawing.coords(self.id)
            x0 = a[0]
            y0 = a[1]
            for i in range(0, len(a), 2):
                x = a[i] - x0
                y = a[i+1] - y0
                a[i] = x0 + x * math.cos(theta) - y * math.sin(theta)
                a[i+1] = y0 + x * math.sin(theta) + y * math.cos(theta)
            Canvas.drawing.coords(self.id, *a)
    
class CanvasError(Exception): pass


## Top level trace hook [deprecated]

# A not-so-successful attempt to use the Python interpreter's 'displayhook' to
# monitor specified variables.  The idea was going to be to allow users to create
# a monitor window, and after every Python command have the monitor redraw values
# it was watching.  The problem is the hook is not called after assignment
# statements....

# import sys

# def start_tracing():
#     sys.displayhook = trace_hook
#     
# def stop_tracing():
#     sys.displayhook = sys.__displayhook__
# 
# def trace_hook(value):
#     print("trace...")
#     sys.__displayhook__(value)
# 
