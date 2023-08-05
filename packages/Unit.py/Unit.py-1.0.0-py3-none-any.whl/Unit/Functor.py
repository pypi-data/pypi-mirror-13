#!/usr/bin/env python

"""
Object Chaining and Accumulation
* Based on Monad things

Concept:
    Take a value, 'z', and permit 
    operations to be performed upon it inline
    "Unit" is the base-class in which operations 
    will be pipelined upon

    In this example, the 'x' variable will be a 
    Unit containing 'z'

    x = Unit(z)

    With the unit we can apply operations

    x.apply(f) = f(x)

    The 'or' operator was picked to be the prefix 
    operator

    x.apply(f) = x | f
    
    Chaining multiple expressions will result in

    x.apply(f).apply(g).apply(h) = x | f | g | h

    Otherwise it would look something like 

    h(g(f(x)))
"""

# Start with a unit class...
class Unit(object):
    """
    The Unit class to contain information 
    within a context. Operations can be 
    applied and composed with cleaner syntax.
    """

    # If a lot of objects are created, __slots__ 
    # will restrict the attributes of the class
    __slots__ = ['acc']

    # Take in a value; if it's a tuple, take the tup
    def __init__(self, *value):
        if len(value) > 1:
            self.acc = value
        else:
            self.acc = value[0]

    # Apply and return the object after an op
    # Check if we're storing a tuple or not before apply
    # Since we don't have special rules, if you want the 
    # "true" value of the Unit, pass in last a True
    # ie: Unit(4) | True == int(4) 
    def apply(self, function):
        if function == True:
            return self.id()
        elif function == False:
            return None
        if isinstance(self.acc, tuple):
            self.acc = function(*self.acc)
        else:
            self.acc = function(self.acc)
        return self

    # Return the pure data without context (must be used)
    def id(self):
        return self.acc

    # The '|' operator
    def __or__(self, function):
        return self.apply(function)

    # str and repr representations
    def __str__(self):
        return "{}".format(self.acc.__str__())

    def __repr__(self):
        return "Unit({})".format(repr(self.acc))

    def __eq__(self,other):
        return self.acc == other.acc


# end
