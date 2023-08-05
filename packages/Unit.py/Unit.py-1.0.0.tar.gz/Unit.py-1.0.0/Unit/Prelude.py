#!/usr/bin/env python

"""
Prelude.py

Aimed to recreate some basic functions from 
GHC's "Prelude" collection

Included in this package:
    * Typeclass definition dictionary
    * Typechecking functions
    * Basic Prelude collection for Unit calculations
"""

# Typeclass stuff
# Use these to enforce rules amongst Unit functions
# Int    - units that represent whole numbers (int, bool)
# Num    - numbers used in math (ints, floats, comp)
# Real   - numbers that are non-imaginary (ints, floats)
# Ord    - types that can be ordered based on their value(s)
# Enum   - types that have positions or storage of some kind
# Fold   - values that can gain or lose shape
# String - supports only the string-type (strings != lists)
# Any    - supports any type, literally
Int, Num, Real, Ord, Enum, Fold, String, Any = range(8)

# TODO: does this system allow modularity/extendability non-builtins?
typeclasses = {
        Int    : (int, bool),
        Num    : (int, float, complex),
        Real   : (int, float),
        Ord    : (int, float, complex, bool, str, list, bytes),
        Enum   : (list, tuple, set, frozenset, dict, str),
        Fold   : (int, float, complex, bool, list, tuple, str, bytes),
        String : (str,),
        Any    : (object,),
}

def get_types(cls):
    """
    get_types :: Int -> [a]
    Return the types belonging to a typeclass
    """
    if cls not in typeclasses:
        raise Exception("get_types() - Type doesn't exist")
    return typeclasses[cls]

# Typeclass check functions
def is_type(cls, *value):
    """
    is_type :: Int -> a -> Bool
    Check if value(s) belongs in a typeclass
    """
    return any((isinstance(v, c) for v in value for c in typeclasses[cls]))

def isnt_type(cls, *value):
    """
    isnt_type :: Int -> a -> Bool
    Wrapper for is_type so you can avoid writing "not is_type"
    """
    return not is_type(cls, *value)

# A curried version of is_type so you can pass it to Unit values
def type_of(cls):
    """
    type_of :: Int -> a -> Bool
    """
    def itype(data):
        return is_type(cls, data)
    return itype

def type_not(cls):
    """
    type_not :: Int -> a -> Bool
    Inverse type_of for Unit operations
    """
    return not type_of(cls)

# This essentially returns the entire Unit container
def id(*data):
    """
    id :: a -> a
    A mathematical "id" function to return what was passed
    """
    if len(data) > 1:
        return data
    else:
        return data[0]

# Equivalent to putStrLn from Haskell.GHC
def puts(data):
    """
    puts :: String -> IO ()
    Will always return None
    """
    print(data)

# Head and Tail from Haskell.GHC
def head(data):
    """
    head :: [a] -> [a]
    Return the first item in an Enumerable type
    If data is not a list type, return it
    """
    if isnt_type(Enum, data):
        return data
    return data[0]

# Tail will be undefined (None) if not a list
def tail(data):
    """
    tail :: [a] -> [a]
    Return the tail (everything after the first)
    If data is not a list, return None
    """
    if isnt_type(Enum, data):
        return None
    return data[1:]

# Take a number of elements from a list
def take(amount):
    """
    take :: Int -> [a] -> [a]
    Take a number of elements from an Enumerable
    If the unit data is not a list, return None
    """
    if isnt_type(Num, amount):
        raise Exception("take() - value given not an Integer")
    def itake(data):
        if not isinstance(data, list):
            return None
        return data[:amount]
    return itake

# Drop a number of elements from a list
def drop(amount):
    """
    drop :: Int -> [a] -> [a]
    Drop values and return the remainder
    If the unit data is not a list, return None
    """
    if not isinstance(amount, int):
        raise Exception("drop() - value given not an Integer")
    def idrop(data):
        if not isinstance(data, list):
            return None
        return data[x:]
    return idrop

# Successor of a value (increment on Int)
def succ(value):
    """
    succ :: Num a => a -> a
    Return the successor of the given value
    """
    if isnt_type(Num, value):
        raise Exception("succ() - value not Ord class")
    return value + 1

# Predecessor of a value (decrement on Int)
def pred(value):
    """
    pred :: Num a => a -> a
    Return the predecessor of the given value
    """
    if isnt_type(Num, value):
        raise Exception("pred() - value not Ord class")
    return value - 1

# Redefine common math ops so we can enforce types 
def add(left_value, right_value):
    """
    add :: Fold a => a -> a -> a
    Add together two values (can be non-numerical)
    """
    if isnt_type(Fold, left_value, right_value):
        raise Exception("add() - Non-foldable types given")
    return left_value + right_value

def sub(left_value, right_value):
    """
    sub :: Num a => a -> a -> a
    Subtract two values and return the difference
    """
    if isnt_type(Num, left_value, right_value):
        raise Exception("sub() - Non-numeric types given")
    return left_value - right_value

def mul(left_value, right_value):
    """
    mul :: Num a => a -> a -> a
    Multiply two values together and return the product
    """
    if isnt_type(Num, left_value, right_value):
        raise Exception("mul() - Non-numeric types given")
    return left_value * right_value

def div(left_value, right_value):
    """
    div :: Num a => a -> a -> a
    Divide one number by another, except when right_value == 0
    """
    if isnt_type(Num, left_value, right_value):
        raise Exception("div() - Non-numeric types given")
    if right_value == 0:
        raise ZeroDivisionError
    return left_value / right_value

# Negate a value (Unit(5) | negate => -5)
def neg(value):
    """
    neg :: Num a => a -> a
    Negate a numerical value (-x)
    """
    if isnt_type(Num, value):
        raise Exception("div() - Non-numeric types given")
    return (-value)

# Even and odd, only works for Real numbers
def odd(value):
    """
    odd :: Real a => a -> Bool
    Determine if a number is odd or not
    """
    if isnt_type(Real, value):
        raise Exception("odd() - non-real type given")
    return bool(value & 1)

def even(value):
    """
    even :: Real a => a -> Bool
    Determine if a number is even or not
    """
    if isnt_type(Real, value):
        raise Exception("even() - non-real type given")
    return bool(not value & 1)

# Exponentiate a number by a number
# Curries pow(x,y)
def expo(value):
    """
    expo :: Num a => a -> a -> a
    Exponentiate a number by an exponent
    """
    def iexp(base):
        if isnt_type(Num, value, base):
            raise Exception("expo() - invalid input")
        return pow(base, value)
    return iexp

# Square a number (wraps pow)
def square(value):
    """
    square :: Num a => a -> a
    Square a number (wraps around expo())
    """
    if isnt_type(Num, value):
        raise Exception("square() - invalid input")
    return pow(value, 2)

# Cubes a number (wraps pow)
def cube(value):
    """
    cube :: Num a => a -> a
    Cube a number (wraps around expo())
    """
    if isnt_type(Num, value):
        raise Exception("cube() - invalid input")
    return pow(value, 3)

# Scale a list of numbers by a scalar
# If we run into a non-numeric type, raise exception
def scale(value):
    """
    scale :: Num a => a -> [a] -> [a]
    """
    def iscale(data):
        res = list()
        try:
            for x in data:
                res.append(x*value)
            return res
        except Exception as e:
            raise Exception("scale() - non-numeric type encountered")
    return iscale

# Take a function with no arguments and 
# collects the results a number of times
def collect(amount):
    """
    collect :: (a) -> Int -> [a]
    Call a non-argument function N times and 
    return the results (ie. random.random())
    """
    def icoll(fun):
        res = list()
        for x in range(amount):
           res.append(fun())
        return res
    return icoll

# Span a list from 0 to x
# Usage: Unit(10) | span => [0..10]
def span(value):
    """
    span :: Int -> [Int]
    Create a span of numbers from 0 to N
    """
    if isnt_type(Int, value):
        raise Exception("span() - invalid range type")
    return list(range(value))

# Create a list from beginning to end
# Desired use: Unit(0) | to(10) => [0..10]
def to(end):
    """
    to :: Int -> Int -> [Int]
    Create a range of numbers from X to Y
    """
    def ito(begin):
        if isnt_type(Int, begin, end):
            raise Exception("to() - invalid range types")
        return list(range(begin, succ(end)))
    return ito

# Wrap len() over an object that may or may 
# not be a list
# Usage: Unit(100) | span | select(odd) | length => 50
def length(data):
    """
    length :: Enum t => t a -> Int
    Return the length of an Enumerable type
    If not enumerable, return 1
    """
    if is_type(Enum, data):
        return len(data)
    return len([data])

# Apply a map to the data
# If the data isn't a list, turn it into one
def fmap(func):
    """
    fmap :: Enum f => (a -> b) -> f a -> f b
    Map a function across a functor
    Similar to builtins.map()
    """
    def imap(data):
        if not isinstance(data, list):
            return list(map(func, [data]))
        return list(map(func, data))
    return imap

# Select elements where predicate is true
# Wrapper for filter()
# Usage: Unit(100) | span | select(odd) => (all odds) 
def select(func):
    """
    select :: (a -> Bool) -> [a] -> [a]
    Grab elements based on a filter function
    Similar to builtins.filter()
    """
    def imap(data):
        if not isinstance(data, list):
            return list(filter(func, [data]))
        return list(filter(func, data))
    return imap

### Comparison operators (shorthand filters)
def comp(comp_fun):
    """
    comp :: (a -> a -> Bool) -> a -> [a] -> [a]
    Comp serves as the higher-order for comparison operators
    Use the shortcut functions like gt() for better results
    """
    def inner1(value):
        def inner2(data):
            if not isinstance(data, list):
                return list(filter(comp_fun, [data]))
            return list(filter(comp_fun, data))
        return inner2
    return inner1

# Comparison shortcut functions
def lt(y):
    """
    lt :: a -> [a] -> [a]
    Grab all values less than Y
    """
    return comp(lambda x: x < y)(y)

def lte(y):
    """
    lte :: a -> [a] -> [a]
    Grab all values less than or equal to Y
    """
    return comp(lambda x: x <= y)(y)

def gt(y):
    """
    gt :: a -> [a] -> [a]
    Grab all values greater than Y
    """
    return comp(lambda x: x > y)(y)

def gte(y):
    """
    gte :: a -> [a] -> [a]
    Grab all values greater than or equal to Y
    """
    return comp(lambda x: x >= y)(y)

def equals(y):
    """
    equals :: a -> [a] -> [a]
    Grab all values equal to Y
    """
    return comp(lambda x: x == y)(y)

def nequals(y):
    """
    nequals :: a -> [a] -> [a]
    Grab all values not equal to Y
    """
    return comp(lambda x: x != y)(y)

# Zipping with Units
def zip_with(zipper):
    """
    zip_with :: [a] -> [b] -> [(a,b)]
    Take two lists and zip them together to produce a pair-list
    """
    def izip(data):
        if isnt_type(Enum, data):
            return list(zip([data], zipper))
        return list(zip(data, zipper))
    return izip

# The return of the "reduce" operation
def reduce(func):
    """
    reduce :: Fold a => (a -> a -> a) -> [a] -> a
    Reduce a list to binary operations and return the result
    ie: Unit(10) | span | reduce(add) = sum(range(10))
    see functools.reduce for more info
    """
    def ired(data):
        accum = None
        if isnt_type(Enum, data):
            data = list(data)
        for x in data:
            if accum is None:
                accum = x
            else:
                accum = func(accum, x)
        return accum
    return ired

# concat function
# Essentially the same as a reduce operation
# Lists and strings both have + ops
def concat(data):
    """
    concat :: Fold a => [[a]] -> [a]
    Join a list of lists into a singular list
    """
    return reduce(add)(data)

# String functions
# Since string isn't a list, additional ops 
# are required for more functionality

# String split
def split(value):
    """
    split :: String a -> a -> a -> [a]
    Split a string into a list of strings based on the seperator
    """
    def isplit(data):
        if isnt_type(String, value, data):
            raise Exception("split() - non-string arguments")
        return data.split(value)
    return isplit

# Join function
# Inverse of string split (in a way)
def join(value=""):
    """
    join :: String a => a -> [a] -> a
    Join together a list of strings by a seperator
    """
    def isplit(data):
        if isnt_type(String, value):
            raise Exception("join() - non-string argument")
        if isnt_type(Enum, data):
            raise Exception("join() - non-list supplied")
        return value.join(data)
    return isplit

# The functions below might need os.linesep instead of '\n' if needed
# lines function
# Similar to GHC.lines
def lines(data):
    """
    lines :: String a => a -> [a]
    Break a string up into a list of strings separated by newline
    """
    return split('\n')(data)

# unlines function
# Similar to GHC.unlines
# Inverse of lines
def unlines(data):
    """
    unlines :: String a => [a] -> a
    Join a list of strings back into a singular string
    """
    return join('\n')(data)

# words function
# Similar to GHC.words
def words(data):
    """
    words :: String a => a -> [a]
    Cut a string into a list of words seperated by whitespace
    """
    return split(' ')(data)

# unwords function
# Similar to GHC.unwords, inverse of words
def unwords(data):
    """
    unwords :: String a => [a] -> a
    Merge a list of strings into a singular string
    """
    return join(' ')(data)

# end
