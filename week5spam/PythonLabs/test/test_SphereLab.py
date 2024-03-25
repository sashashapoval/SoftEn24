import unittest

from PythonLabs.SphereLab import *
import math
from copy import copy

class SphereTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\nSphereLab:  ", end = "")
    
    # Vector arithmetic.  Note: calls to assert_equal will also test the == method.
    
    def test_01_vectors(self):
        v1 = Vector(1, 1, 1)
        v2 = Vector(2, 2, 2)
        v3 = Vector(3, 3, 3)

        self.assertEqual(v3, v1 + v2)
        self.assertEqual(v1, v3 - v2)
        self.assertEqual(v2, v1 * 2)

        v3 += v1
        self.assertEqual(v3, Vector(4, 4, 4))
        v3 -= v1
        self.assertEqual(v3, Vector(3, 3, 3))
        v3 *= 2
        self.assertEqual(v3, Vector(6, 6, 6))

        self.assertAlmostEqual(v2.norm(), sqrt(12))
        
        v3.clear()
        self.assertEqual(0, v3.x)
        self.assertEqual(0, v3.y)
        self.assertEqual(0, v3.z)
        
        v4 = Vector(1,0,0)
        v5 = Vector(0,1,0)
        self.assertAlmostEqual(math.pi/2, v4.angle(v5))
        self.assertAlmostEqual(math.pi/4, v1.angle(v4))     # Note: method ignores z...
        self.assertAlmostEqual(0, v1.angle(v1))
        
    # Make two body objects, test calculation of force attraction between them,
    # verify movement is equal magnitude and in opposite direction (i.e. bodies move 
    # toward each other on the y axis).  Also tests the clear_force and copy methods.

    def test_02_bodies(self):
        y1 = 1000
        y2 = 0
        b1 = Body(1000000, Vector(0, y1, 0), Vector(0, 0, 0))
        b2 = Body(1000000, Vector(0, y2, 0), Vector(0, 0, 0))
        b1.add_force(b2)
        b2.add_force(b1)
        b1.move(100)
        b2.move(100)
        self.assertEqual(b1.position.x, 0.0)
        self.assertEqual(b2.position.x, 0.0)
        self.assertAlmostEqual((y1 - b1.position.y), (b2.position.y - y2))
        self.assertEqual(b1.position.z, 0.0)
        self.assertEqual(b2.position.z, 0.0)
        b1.clear_force()
        self.assertEqual(b1.force, Vector(0,0,0))

        b3 = b1.copy()                # test to make sure deep copy was made
        b3.mass = 0
        self.assertNotEqual(b3.mass, b1.mass)
        self.assertEqual(b3.position, b1.position)
        self.assertEqual(b3.velocity, b1.velocity)

    # Same as above, but use the class method (which does the calculation once and
    # uses the same force twice)

    def test_03_interaction(self):
        y1 = 1000
        y2 = 0
        b1 = Body(1000000, Vector(0, y1, 0), Vector(0, 0, 0))
        b2 = Body(1000000, Vector(0, y2, 0), Vector(0, 0, 0))
        Body.interaction(b1, b2)
        b1.move(100)
        b2.move(100)
        self.assertEqual(b1.position.x, 0.0)
        self.assertEqual(b2.position.x, 0.0)
        self.assertAlmostEqual((y1 - b1.position.y), (b2.position.y - y2))
        self.assertEqual(b1.position.z, 0.0)
        self.assertEqual(b2.position.z, 0.0)

    # Test the Body class by doing a mini-simulation of bodies based on the sun and
    # inner planets of the solar system.  Uses coordinates based on the JPL ephemeris
    # for Jan 1 1970.  Run for 88 time steps, with dt = 1 day.  Expect Mercury to be 
    # close to where it started.  

    def test_04_solar_system(self):
        bodies = [
          Body(1.989E30, Vector(0,0.000E00,0), Vector(0.000E0,0,0), "sun"),
          Body(3.303E23, Vector(3.83E+10, 2.87E+10, -1.17E+09), Vector(-38787.67,  41093.05,  6918.461), "mercury"),
          Body(4.870E24, Vector(-5.37E+09, -1.08E+11, -1.16E+09), Vector(34741.48, -1865.747, -2031.506), "venus"),
          Body(5.976E24, Vector(-2.70E+10, 1.44E+11, 9686451), Vector(-29770.44, -5568.042, 0.3961261), "earth"),
          Body(6.421E23, Vector(1.98E+11, 7.42E+10, -3.33E+09), Vector(-7557.626,  24761.27,  704.7457), "mars")
        ]

        mercury = bodies[1]

        dt = 86459            # number of seconds in a day (at 365.25 days/year)
        nb = len(bodies)      # number of bodies
        nt = 88               # number of time steps (simulated days); 88 is enough for 1 orbit for Mercury

        mercury_start = copy(mercury.position)

        for t in range(nt):                 # main simulation loop
            for i in range(nb):             # compute all pairwise interactions
                for j in range(i+1, nb):
                    Body.interaction( bodies[i], bodies[j] )

            for b in bodies:
                b.move(dt)                  # apply the accumulated forces
                b.clear_force()             # reset force to 0 for next round

        self.assertTrue(abs(mercury_start.x - mercury.position.x) < 1e10)
        self.assertTrue(abs(mercury_start.y - mercury.position.y) < 1e10)
        self.assertTrue(abs(mercury_start.z - mercury.position.z) < 1e10)

    # Test the Turtle class by making a "turtle" and moving it in a square pattern.

    def test_05_turtle(self):
        t = Turtle( x = 0.0, y = 0.0, heading = 0.0, speed = 10.0)

        # move up 10 paces
        t.advance(1)        
        self.assertAlmostEqual(t.position.x,  0.0)
        self.assertAlmostEqual(t.position.y, 10.0)

        # turn, move right 10 paces
        t.turn(90)
        self.assertAlmostEqual(t.heading(), 90.0)
        t.advance(1)        
        self.assertAlmostEqual(t.position.x, 10.0)
        self.assertAlmostEqual(t.position.y, 10.0)

        # turn, move down 10 paces
        t.turn(90)
        self.assertAlmostEqual(t.heading(), 180.0)
        t.advance(1)        
        self.assertAlmostEqual(t.position.x, 10.0)
        self.assertAlmostEqual(t.position.y,  0.0)

        # turn, move left 10 paces
        t.turn(90)
        self.assertAlmostEqual(t.heading(), 270.0)
        t.advance(1)        
        self.assertAlmostEqual(t.position.x,  0.0)
        self.assertAlmostEqual(t.position.y,  0.0)

    # Create the 2-body melon/earth system, test the simulation

    def test_06_melon(self):
        b = make_system(path_to_data('melon.txt'))
        melon = b[0]
        
        melon.set_height(30)
        self.assertAlmostEqual(melon.height(), 30.0, "melon not 30 meters up")
        melon.set_height(100)
        self.assertAlmostEqual(melon.height(), 100.0, "melon not 100 meters up")
        self.assertAlmostEqual(drop_melon(b, 0.1), 4.5, "expected 4.5 seconds to fall 100 meters")
