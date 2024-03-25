# SphereLab -- Simple N-Body simulation of the solar system

# __all__ = [ ]

import PythonLabs
from .Canvas import Canvas
from .Tools import classname, path_to_data

from math import sqrt, radians, degrees, sin, cos, acos
import os
from copy import copy, deepcopy

class RobotError(Exception):  pass

class Vector:
    """
    [SphereLab] A Vector is a 3-tuple of (x,y,z) coordinates.  The following operators are 
    defined for vector objects (v is a vector and a is a scalar):
       v == v
       v + v
       v - v
       v * a
       v.norm()
       v.angle(v)
    """
    def __init__(self, *args):
        "Make a new vector with the specified x, y, and z components."
        self.x, self.y, self.z = args
    
    def __repr__(self):
        return "(%.5g, %.5g, %.5g)" % (self.x, self.y, self.z)

    def __eq__(self, other):
        "Two vectors are the same if all three components are the same."
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __add__(self, other):
        "Create a new vector that is the sum of this vector and another vector."
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        "Create a new vector that is the difference between this vector and another vector."
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, a):
        "Create a new vector that is the product of this vector and scalar a."
        return Vector(self.x *a, self.y * a, self.z * a)
        
    def coords(self):
        """
        Return a tuple of three numbers corresponding to the x, y, and z
        components of this vector.
        """
        return (self.x, self.y, self.z)

    def norm(self):
        "Compute the magnitude (Euclidean norm) of this vector."
        return sqrt( self.x ** 2 + self.y **2 + self.z **2 )

    def angle(self, other):
        """
        Compute the angle between this vector and another vector.  This method is
        only used when drawing 2D vectors, so the z dimension is ignored.
        """
        n1 = sqrt(self.x ** 2 + self.y ** 2)
        n2 = sqrt(other.x ** 2 + other.y ** 2)
        return acos((self.x * other.x + self.y * other.y) / (n1 * n2))
        
    def clear(self):
        "Set the vector to (0,0,0)"
        self.x = self.y = self.z = 0

# The universal gravitational constant, assuming mass is in units of kilograms, distances 
# are in meters, and time is in seconds.

G = 6.67E-11

class Body:
    """
    [SphereLab] A Body object represents the state of a celestial body.  A body has mass 
    (a scalar), position (a vector), and velocity (a vector).  A third vector, named force, 
    is used when calculating forces acting on a body.  The size and color attributes are 
    used by the visualization methods.
    """
    def __init__(self, mass = 0, position = Vector(0,0,0), velocity = Vector(0,0,0), name = None):
        """
        Create a new Body object with the specified mass (a scalar), position (a vector), 
        and velocity (another vector).  A fourth argument is an optional name for the body.
       """
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.name = name
        self.force = Vector(0,0,0)

    def __repr__(self):
        if self.name:
            return "%s m: %.3g r: %s v: %s" % (self.name, self.mass, self.position, self.velocity)
        else:
            return "m: %.3g r: %s v: %s" % (self.mass, self.position, self.velocity)
#         s = "<" + classname(self)
#         if self.name: s += " " + self.name
#         s += " m: %.3g r: %s v: %s" % (self.mass, self.position, self.velocity)
#         s += ">"
#         return s
    
    def copy(self):
        "Make a copy of this body."
        return deepcopy(self)

    def clear_force(self):
        """
        Reset the force vector to (0,0,0).
        """
        self.force.clear()

    def add_force(self, other):
        """
        Compute the force exerted on this body by another body and update this body's 
        force vector.
        """
        r = self.position - other.position
        nr = r.norm() ** 3
        mr = other.mass / nr
        self.force += r * mr

    def move(self, dt):
        """
        Update this body's position by applying the current force vector for dt seconds.
        """
        acc = self.force * G * -1.0
        self.velocity += acc * dt  
        self.position += self.velocity * dt

    @staticmethod
    def interaction(b1, b2):
        """
        This class method will compute the interaction between bodies b1 and b2 and
        update their force vectors.  Since the forces on the bodies are the same, but 
        acting in the opposite direction, the force can be calculated just once and 
        then used to update both bodies.
        """
        r = b1.position - b2.position
        a = r.norm() ** 3
        b1.force += (r * (b2.mass / a))
        b2.force += (r * (-b1.mass / a))
        
class VBody(Body):
    """
    [SphereLab] The VBody class is an extension of the Body class with attributes for
    drawing and moving a body on the canvas.
    """
    def __init__(self, mass, position, velocity, name, size = 5, color = 'lightblue'):
        super().__init__(mass, position, velocity, name)
        self.size = size
        self.color = color
        self.graphic = None
        
    def draw(self, x, y):
        """
        Create the graphic for this body, save its current location (used to draw
        tracks when the body moves).
        """
        self.graphic = Canvas.Circle(x, y, self.size, fill = self.color)
        self.prevx = x
        self.prevy = y
        self.pendown = True
        
    def move(self, dt):
        """
        If the body has a graphic move it (not all bodies in a simulation are on the
        canvas, e.g. outer planets in a solar system simulation might not be displayed).
        """
        super().move(dt)
        if self.graphic:
            newx, newy = scale(self.position, Canvas.view.origin, Canvas.view.scale)
            Canvas.move(self.graphic, newx-self.prevx, newy-self.prevy, self.pendown)
            self.prevx = newx
            self.prevy = newy
            self.pendown = not self.pendown

    def copy(self, color = None):
        "Make a copy of this body, assigning its graphic a new color if specified."
        clone = deepcopy(self)
        if self.graphic:
            if color == None:  color = self.color
            clone.graphic = Canvas.Circle(self.prevx, self.prevy, self.size, fill = color)
        return clone

# Turtle graphics (used in robot simulation)
           
class Turtle:
    """
    [SphereLab]  This class implements a rudimentary "turtle graphics" system.  A 
    turtle is an object that moves around on a canvas under direction from a user
    that tells it to advance, turn, etc.  A turtle also has a "pen" that can be raised 
    or lowered.  When the pen is down, the turtle draws a line on the canvas as it 
    moves.
    """
    def __init__(self, x = 0, y = 0, heading = 0, speed = 10, track = False):
        alpha = radians(heading + 90)
        self.position = Vector(x, y, 0)
        self.velocity = Vector( -speed*cos(alpha), speed*sin(alpha), 0 )
        self.graphic = None
        self.reference = None
        self.tracking = track

    def __repr__(self):
        return "<%s at (%d,%d)>" % (classname(self), self.position.x, self.position.y)
        
    # Define a vector pointing due north to use in calculating a Turtles heading
    # (direction of travel).

    north = Vector(0, 10, 0)
    
    def heading(self):
        """
        Return the current heading, in compass degrees, of this turtle object.  The 
        heading is a number between 0 and 360, where 0 is north, 90 is east, etc.
        """
        d = degrees(self.velocity.angle(Turtle.north))
        if self.velocity.x < 0:
            return (360 - d)
        else:
            return d
      
    def speed(self):
        "Return the current speed (in meters per second) of this turtle object."
        return self.velocity.norm()
        
    def location(self):
        "Return the x and y coordinate's of the turtle's location"
        return (self.position.x, self.position.y)
        
    def turn(self, alpha):
        "Reorient the turtle by telling it to turn clockwise by alpha degrees."
        theta = -radians(alpha)
        x = self.velocity.x * cos(theta) - self.velocity.y * sin(theta)
        y = self.velocity.x * sin(theta) + self.velocity.y * cos(theta)
        self.velocity.x = x
        self.velocity.y = y
        if self.graphic:
            self.graphic.rotate(alpha)
          
    def advance(self, dt):
        "Tell the turtle to move straight ahead from its current position for dt seconds."
        prevx = self.position.x
        prevy = self.position.y
        self.position += self.velocity * dt
        if self.graphic:
            Canvas.move(self.graphic, self.position.x-prevx, prevy-self.position.y, track = self.tracking)
            
    def set_reference(self, x, y):
        "Set the reference point (used to orient the turtle) to the specified coordinate"
        self.reference = (x, y)
        
    def orient(self):
        """
        Tell the turtle to rotate until its heading is orthogonal to a reference point.
        See the Lab Manual for details about setting a reference point and how the 
        orientation is calculated.
        """
        if self.reference == None:
            raise ValueError("no reference point")
        mx, my = self.reference
        tx, ty = self.position.x, self.position.y
        mid = Vector(tx-mx, ty-my, 0.0)
        theta = degrees(mid.angle(self.velocity))
        alpha = 2 * (90.0 - theta)
        self.turn(alpha)
        
    def plant_flag(self):
        set_flag_location(self.position.x, self.position.y)
        
# Robot visualization

_robot_view_options = {
    'canvas_size' : 400,
    'polygon' : (4,0,0,10,4,8,8,10),
    'flag' : False,
    'track' : False,
}

class RobotView:
    def __init__(self, turtle, options):
        self.turtle = turtle
        self.options = options

def view_robot(turtle = None, **view_options):
    """
    [SphereLab] Initialize the PythonLabs Canvas for an experiment with the robot 
    explorer.  The canvas will show a map of an area 400 x 400 meters and the robot 
    (represented by a Turtle object) on the west edge, facing north.  Options:
        turtle:       the Turtle object to use in the drawing; if no object is 
                      passed, one is created using the polygon option
        polygon:      a sequence of coordinates to define the shape of the robot
                      (default: (4,0,0,10,4,8,8,10) )
        canvas_size:  number of pixels on each side of the canvas 
                      (default: 400)
        flag:         if True set a reference point in the middle of the canvas
                      (default: False)
        track:        if True tell the robot to leave tracks showing its path
                      (default: False)
    The value returned by view_options is a reference to the Turtle object on the
    canvas (either the object passed as an argument or the one created by default).
    """
    options = dict(_robot_view_options)
    options.update(view_options)

    poly = list(options['polygon'])
    edge = options['canvas_size']
    for i in range(0, len(poly), 2):
        poly[i] += edge/10
        poly[i+1] += edge/2
    Canvas.init(edge, edge, "SphereLab::Robot")
    Canvas.delay = 0.01

    if turtle == None:
        turtle = Turtle(x = edge/10, y = edge/2, heading = 0, speed = 10)
    if turtle.graphic == None:
        turtle.graphic = Canvas.Polygon(poly, outline = 'black', fill = '#00ff88')
    Canvas.register(RobotView(turtle, options)) 
    
    if options['flag']:  
        set_flag_location(edge/2, edge/2)
    if options['track']: 
        turtle.tracking = True
        
    return turtle
    
def set_flag_location(x = None, y = None):
    """
    [SphereLab] Place a flag at the specified location.  If no coordinates are given
    the flag will be placed in the middle of the canvas.
    """
    if x == None or y == None:
        if Canvas.view == None:
            raise RobotError("call view_robot to initialize the canvas")
        dim = Canvas.view.options['canvas_size']
    if x == None:  x = dim / 2
    if y == None:  y = dim / 2
    if Canvas.view != None:
        r = 3.0
        Canvas.Circle( x + r/2, y + r/2, r, fill = 'darkblue' )
        Canvas.view.turtle.set_reference(x, y)

# Earth-melon visualization

class HBody(VBody):
    """
    [SphereLab] The HBody class is an extension of the VBody (visualized body)
    class to include a height method used in simulations where a body's motion
    should stop when it hits the ground. 
    """
    def __init__(self, b):
        super().__init__(b.mass, b.position, b.velocity, b.name, b.size, b.color)
        self.ground = self.position.y
        self.hmax = None
    
    def draw(self, mxmin, mymin, mymax, hmax):
        """
        Draw the circle for this body, and save parameters used to update the drawing
        when the body moves (mxmin = initial left edge, mymin = highest upper edge,
        mymax = lowest bottom edge, hmax = highest simulated height)
        """
        self.scale = (mymax-mymin) / hmax
        self.hmax = hmax
        self.mymax = mymax
        height = self.position.y - self.ground
        x = mxmin
        y = mymax = mymax - height * self.scale
        self.graphic = Canvas.Circle(x, y, self.size, fill = self.color)
        self.pendown = True
    
    def set_height(self, height):
        """
        Position the body at the specified height above the ground.  If the body is
        on the canvas move the circle to indicate the new height.
        """
        if height < 0 or self.hmax and height > self.hmax:
            raise ValueError("height must be between 0 and %d meters" % self.hmax)
        self.position.y = self.ground + height
        self.velocity.y = 0.0
        if self.graphic:
            mcoords = Canvas.drawing.coords(self.graphic.id)
            mcoords[3] = self.mymax - height * self.scale + self.size
            mcoords[1] = mcoords[3] - 2 * self.size
            Canvas.drawing.coords(self.graphic.id, *mcoords)
            
    def height(self):
        """
        Return the current height (distance above the ground).
        """
        return self.position.y - self.ground
        
    def move(self, dt):
        """
        Compute the force due to gravity (by calling a superclass method), and if
        the body is on the screen update to show its new position.
        """
        if self.height() > 0:
            x, y = self.position.x, self.position.y
            Body.move(self,dt)                              # bypass the VBody move
            if self.graphic:
                dx = (self.position.x - x) * self.scale
                dy = (y - self.position.y) * self.scale
                Canvas.move(self.graphic, dx, dy, self.pendown)
                self.pendown = not self.pendown
        
_melon_view_options = {
    'canvas_size' : 400,
    'mxmin' : 100,                  # left edge of melon on screen
    'mymin' : 50,                   # top of highest position of melon on screen
    'hmax' : 100,                   # max height (in meters) of simulated melon
}

class MelonView:
    def __init__(self, bodies, options):
        self.bodies = bodies        # two bodies used in simulation
        self.options = options      # drawing options

def view_melon(blist, **view_options):
    """
    [SphereLab] Initialize the canvas to show a drawing of a '2-body system' with 
    a small circle to represent a watermelon and a much larger partial circle for the
    earth.  The required argument is a list of two Body objects representing the melon 
    and earth, respectively.
    """
    options = dict(_melon_view_options)
    options.update(view_options)

    edge = options['canvas_size']
    mxmin = options['mxmin']
    mymin = options['mymin']
    hmax = options['hmax']
    Canvas.init(edge, edge, "SphereLab::Melon")
    
    earth = Canvas.Circle(200, 2150, 1800, fill = blist[1].color)   # draw the earth
    mymax = Canvas.drawing.coords(earth.id)[1]
    blist[0].draw(mxmin, mymin, mymax, hmax)                        # draw the melon

    Canvas.register(MelonView(blist, options))
    Canvas.delay = 0.01
    
def drop_melon(b, dt):
    """
    [SphereLab] Repeatedly call step_system to compute a new position for the melon,
    stopping when the melon's height is at or below 0.  Return the simulated time
    the melon fell.
    """
    count = 0
    melon = b[0]
    
    while melon.height() > 0:
        step_system(b, dt)
        count += 1
    
    return count * dt

# N-Body systems

def make_system(filename):
    """
    [SphereLab] Initialize a new n-body system, returning an array of body objects
    based on descriptions in the specified file.
    """
    bodies = [ ]
    # if filename[0] == ':':
    #     filename = os.path.join(PythonLabs.datadir, "spheres", filename[1:])
    with open(filename) as bodyfile:
        for line in bodyfile:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':  continue
            name, mass, rx, ry, rz, vx, vy, vz, diam, color = line.split()
            position = Vector(float(rx), float(ry), float(rz))
            velocity = Vector(float(vx), float(vy), float(vz))
            bodies.append( VBody(float(mass), position, velocity, name, float(diam), color) )
    if filename.find('melon') > 0:
        bodies[0] = HBody(bodies[0])
    return bodies

_step_options = {
    'nsteps' : 1,
    'delay' : 0.01,
}

def step_one(falling, stationary, dt, **step_options):
    """
    [SphereLab] Run one time step of the 'falling body' simulation, moving the falling
    body after computing its interactions with the stationary bodies (but leaving the 
    others where they are).  The third argument is the time step size.
    """
    options = dict(_step_options)
    options.update(step_options)
    
    if Canvas.view:
        Canvas.delay = options['delay']

    for i in range(options['nsteps']):
        for x in stationary:
            Body.interaction( falling, x )

        falling.move(dt)
        falling.clear_force()

        if Canvas.view:
            Canvas.update()

def step_system(bodies, dt, **step_options):
    """
    [SphereLab] Run one time step of a full n-body simulation.  Compute the pairwise 
    interactions of all bodies in the system, update their force vectors, and then 
    move them an amount determined by the time step size dt.
    """
    options = dict(_step_options)
    options.update(step_options)
    
    if Canvas.view:
        Canvas.delay = options['delay']

    nb = len(bodies)

    for i in range(options['nsteps']):
        for i in range(nb):             # compute all pairwise interactions
            for j in range(i+1, nb):
                Body.interaction( bodies[i], bodies[j] )
    
        for b in bodies:
            b.move(dt)                  # apply the accumulated forces
            b.clear_force()             # reset force to 0 for next round
    
        if Canvas.view:
            Canvas.update()

# N-Body visualization

_nbody_view_options = {
    'origin' : 'center',
    'scale' : None,             # specify max, or compute from body coordinates
    'wsize' : 700,
    'dash' : 1,
    'delay' : 0.01,
}

class NBodyView:
    def __init__(self, bodies, origin, scale, options):
        self.bodies = bodies
        self.origin = origin
        self.scale = scale
        self.options = options
        self.dashcount = 0
        self.pendown = False

def view_system(blist, **view_options):
    """
    [SphereLab] Initialize the canvas to show the motion of a set of bodies in an 
    n-body simulation and draw a circle for each body in the list.
    """
    options = dict(_nbody_view_options)
    options.update(view_options)
    Canvas.init(options['wsize'], options['wsize'], "SphereLab::NBody")
    
    if Canvas.view != None and type(Canvas.view) == NBodyView:
        for x in Canvas.view.bodies:
            x.graphic = None
    
    origin = set_origin(options['origin'], options['wsize'])
    sf = set_scale(blist, options['origin'], options['scale'], options['wsize'])
    for b in blist:
        x, y = scale(b.position, origin, sf)
        b.draw(x, y)
    Canvas.register(NBodyView(blist, origin, sf, options))
    Canvas.delay = options['delay']

def set_origin(loc, wsize):
    """
    [SphereLab] Make a vector that defines the location of the origin (in pixels).
    """
    if loc == 'center':
        return Vector(wsize/2, wsize/2, 0)
    else:
        return Vector(0,0,0)
    
def set_scale(blist, origin, scale, wsize):
    """
    [SphereLab] Set the scale factor.  Use the parameter passed by the user, or 
    find the largest coordinate in a list of bodies.    
    """
    if scale == None:
        dmax = 0.0
        for b in blist:
            dmax = max(dmax, max(map(abs,b.position.coords())))
    else:
        dmax = scale
    sf = wsize / 2 if origin == 'center' else wsize
    return (sf / dmax) * 0.8

def scale(vec, origin, sf):
    """
    [SphereLab] Map a simulation's (x,y) coordinates to screen coordinates using 
    the specified origin and scale factor.
    """
    loc = copy(vec)
    loc *= sf
    loc += origin
    return (loc.x, loc.y)
