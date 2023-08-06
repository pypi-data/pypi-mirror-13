#!/usr/bin/env python
# encoding: utf-8
"""Exemple to show how to use it compute all double of a list
@author: Vezin Aurelien
@license: CeCILL-B"""

from multiprocesspool import MultiProcessPool

def double(value):
    return value * 2
    
def queueop(value, vallistres):
    vallistres.append(value)
    return vallistres
    
if __name__ == "__main__":
    pp = MultiProcessPool(double, [ i for i in range(0,100) ], queueop, [])
    print sorted(pp.run(4))
