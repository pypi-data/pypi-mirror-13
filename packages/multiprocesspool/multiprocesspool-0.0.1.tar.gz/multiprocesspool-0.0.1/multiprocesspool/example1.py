#!/usr/bin/env python
# encoding: utf-8
"""Exemple to show how to use it to do the sum of all double of
int in a list
@author: Vezin Aurelien
@license: CeCILL-B"""

from multiprocesspool import MultiProcessPool


def double(value):
    return value * 2
    
def queueop(value, valres):
    valres = valres+value
    return valres
    
if __name__ == "__main__":
    pp = MultiProcessPool(double, [ i for i in range(0,100) ], queueop, 0)
    print pp.run(4)
