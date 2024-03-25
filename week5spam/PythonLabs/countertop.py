
def countertop(x):
    "[PythonLabs] Compute the area of a square counter with a missing wedge."
    square = x ** 2
    triangle = ((x / 2) ** 2) / 2
    return square - triangle

