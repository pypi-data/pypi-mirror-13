#!/usr/bin/env python
# encoding: utf-8
"""multiprocesspool.py contain a class
to used all cores of a computer to do the same operation
on multiple elements of a list  
@author: Vezin Aurelien
@license: CeCILL-B"""

from multiprocessing import Process, Lock, Queue, Value


class MultiProcessPool(object):
    """ ProcessPool allow you to do parallel computation in python
    @ivar operationfunction: the function used to do the same operation
    on any values. Must take a value of values as argument
    @type operationfunction: function
    @ivar queuefunction: the function use to do the same operation
    on any value calculated. Must take a calculated value as argument
    and a element of the return type as parameter
    @type queuefunction: function
    @ivar values: the list of value to use
    @type values: list(anything)
    @ivar valres: the result
    @type valres: anything
    @ivar q: the Queue
    @type q: Queue
    @ivar lock: the lock
    @type lock: Lock
    @ivar position: the current position in the list
    @type position: Value
    """
    
    def __init__(self, operationfunction, values, queuefunction, valres):
        """ set all the class variable
        @param operationfunction: the function used to do the same 
        operation on any values. Must take a value of values as argument
        @type operationfunction: function
        @pram queuefunction: the function use to do the same operation
        on any value calculated. Must take a calculated value as argument
        and a element of the return type as parameter
        @type queuefunction: function
        @param values: the list of value to use
        @type values: list(anything)
        @param valres: the default result (if there is no values in the list)
        @type valres: anything
        """
        self._operationfunction = operationfunction
        self._queuefunction = queuefunction
        self._values = values
        self._valres = valres
        self._q = Queue()
        self._lock = Lock()
        self._position = Value('i', 0)
        
    def _processtarget(self):
        """ The method executed in each process """
        while self._position.value < len(self._values):
            #lock and get the current position in the list
            #then add 1 to the current position and unlock
            self._lock.acquire()
            postemp = self._position.value
            self._position.value = self._position.value +1
            self._lock.release()
            #if we are in the boundary of the list use the function
            #created by the user and send the result in the queue
            if postemp < len(self._values):
                res = self._operationfunction(self._values[postemp])
                self._q.put(res)
    
    def _mapqueue(self):
        """  Save all the queue values in the way we want"""
        for i in range(0, len(self._values)):
            self._valres = self._queuefunction(self._q.get(), 
                                               self._valres)
            
    def run(self, nbprocess):
        """ do the computation
        @param nbprocess: the number of process to create
        @type nbprocess: int"""
        procs = [ Process(target=self._processtarget, args=()) 
                  for i in range(0, nbprocess) ]
        for p in procs:
            p.start()
        self._mapqueue()
        for p in procs:
            p.join()
        return self._valres
