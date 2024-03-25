#! /usr/bin/env python3

def celsius(t):
    "[PythonLabs] Convert temperature t from Fahrenheit to Celsius."
    return (t - 32) * 5 / 9

from sys import argv

if __name__ == '__main__':
   temp = celsius(int(argv[1]))
   print("%.2f\n" % temp)

# print(argv)
# print(__name__)
