Unit.py
========

Quick and dirty function chaining with some 
hidden goodies, inspired by Haskell.

# What the heck is this?

Python's function composition is naturally ugly 
and hideous, so much that they'll probably tell you to 
*not* nest functions within eachother too much.

So here's a way of passing functions to data values 
in a point-free-ish way that's fun and easy.

# Why?

Have you ever had a couple functions and you had to 
nest them together to get a computation? Let's say 
you had these functions.

``` python
def f(x): # do some computation
def g(x): # do another one
def h(x): # etc
def i(x): # ...
```
You wanted to nest these in a way that you got one 
final computation, so here's what you'd do in 
Python naturally.

``` python
# Calculate the value of "x"
final_value = i(h(g(f(x))))
```
Messy, right? Well this happens far too often in 
Python. It's not terribly dynamic because if we 
want to go back and add more functions to the mix, 
we have to wiggle our way through that sea of 
parentheses to add another function.

If instead, we stored our functions in a list:
``` python
funcs = [f, g, h, i]
final_value = None
for func in funcs:
    final_value = func(x)
```
It's dynamic and you can add as many functions as 
you want to the list, but it doesn't look very nice.

Instead, with Unit.py, you can write an expression 
in the following way:
``` python
Unit(x) | f | g | h | i # and so on...
```

This creates a much nicer looking function 
composition that can easily be modified and 
extended upon without much confusion.

# Requirements 

Python 3 is the optimal choice, as it changes 
most functions to produce generators as opposed to 
raw lists. Python 2 can still be used, but it will 
be buggy and issues should be filed immediately.

# Install

From _python-pip_, just run:
```
pip install Unit.py
```

To check if you have it installed:
``` python
import Unit
print(Unit.__version__)
```

To import everything, try this line:
```
from Unit.All import *
```

# Examples

Most examples below will be using functions defined within 
_Unit.Prelude_. _Prelude_ is a package dedicated at mimicking 
most common functions from Haskell GHC's "Prelude" library.

## Hello World

``` python
Unit("Hello world!") | print
```
* _print_ doesn't return a value so we end up with a None
* _print_ also isn't a function in Python 2

In Prelude is a defined print function that works across 
both versions (as a workaround for the keyword syntax).

``` python
Unit("Hello world!") | puts
```

## Number Manipulation

_succ_ and _pred_ are functions that return the 
successor and predecessor values of a number. 

``` python
Unit(4) | succ 
# => Unit(5)

Unit(4) | pred
# => Unit(3)
```

You can also negate numbers using _neg_.

``` python
Unit(5) | neg
# => Unit(-5)
```

## Tuples and Variable Argument Functions

You can store multiple values in a Unit and 
then apply those values to a function. Let's say 
we wanted to add two numbers together:

``` python
Unit(2, 3) | (lambda x, y: x + y)
# => Unit(5)
```

For any function that accepts multiple values as arguments, 
you can use Unit tuples to apply arguments to them. For 
instance, _max_ works:

``` python
Unit(2,3,4,5,6,7,8,9) | max
# => Unit(9)
```

## Lists and List Functions

Lists are a generally good way of doing procedures 
compared to tuples, as more functions take advantage of list 
versus tuples.

To make a list of numbers, we can use a new function _span_ which 
takes a number and gives us a list of numbers. This is 
different from _range_, as _span_ always returns a list. 
In Python 3 this behaviour was changed.

### Creating a List from Scratch
``` python
Unit(10) | span 
# => Unit([0,1,2,3,4,5,6,7,8,9])
```

### Head and Tail of a List
``` python
Unit(5) | span | head
# => Unit(0)

Unit(5) | span | tail
# => Unit([1,2,3,4])
```

### Mapping a Function over a List
``` python
Unit(5) | span | fmap(suc)
# => Unit([1,2,3,4,5])
```

### Filtering elements with a Predicate
``` python
Unit(10) | span | select(even)
# => Unit([0,2,4,6,8])
```

### Length of a List
``` python
Unit(10) | span | length
# => 10
```

### Filtering Numbers Less than a Value
``` python
Unit(10) | span | lt(5)
# => Unit([0,1,2,3,4])
```
Other functions include:
* lte
* gt
* gte
* equals
* nequals

### Take/Drop Elements from a List
``` python
Unit(10) | span | take(5)
# => Unit([0,1,2,3,4])

Unit(10) | span | drop(5)
# => Unit([5,6,7,8,9])
```

### Spawning a Range of Numbers

``` python
Unit(5) | to(10)
# => Unit([5, 6, 7, 8, 9, 10])
```

### List Comprehension
``` python
# Take numbers from 1 to 10, square, take the even numbers
Unit(1) | to(10) | fmap(square) | select(even)
# => Unit([4, 16, 36, 64, 100])

# The equivalent list comp in classic Python would be
[square(x) for x in range(1,11) if even(square(x))]
```
The new Unit version looks something more akin to Ruby 
syntax, but in most cases using Python's list comps are 
better to use for performance (less memory usage).

### Reduce on Lists

The latest feature added is a clone of _functools.reduce_. 
It breaks down the elements of a list into a series of 
binary computations and returns the final result.

``` python
# Finding the sum of a list of data without reduce
Unit(10) | span | sum
# => Unit(45)

# Doing the same thing as sum()
Unit(10) | span | reduce(add)
# => Unit(45)

# Defining our own product() function
Unit(1) | to(11) | reduce(mul)
# => Unit(3628800)

# Factorial of 5
Unit(1) | to(6) | reduce(mul)
# => Unit(120)
```
### Zipping

_zip_ is a cool function that takes in a number of 
lists and zips the values together to form a list of 
tuples, with matching position elements from each list.

Since _zip_ takes in a number of arguments, you have a few 
options of doing zipping.

Method one: using Unit to store the arguments of _zip_, as 
this lets you use any number of lists and returns the correct 
result.
``` python
Unit([1,2],[3,4]) | zip | list
# => Unit([(1,3), (2,4)])
```

Method two: using the new zip_with method that will perform 
a _zip_ action against a Unit and return the _zip_ of the two 
lists. The downside is that this can't be chained to produce 
the same results as a 3-or-more _zip_ call.
``` python
Unit([1,2]) | zip_with([3,4])
# => Unit([(1,3),(2,4)])
```

But if you keep chaining zip_with calls, it produces 
the same output as chaining _zip_ calls.
``` python
# Equivalent to zip(zip([1,2],[3,4]),[5,6])
Unit([1,2]) | zip_with([3,4]) | zip_with([5,6])
# => Unit([((1,3),5),((2,4),6)])
```

### Concatenation

Concatenation in GHC is similar to folding over 
a list of data with an empty array using the concat (++) 
operator. For Python, the __add__ operator is configured 
for both lists and strings, making it a little similar to how 
lists and strings are defined in Haskell.

_concat_ here is defined to be simply _reduce_ with the 
_add_ function over a list of lists or strings.
``` python
Unit([[1],[2]]) | concat
# => Unit([1, 2])

Unit(["hello ", "world"]) | concat
# => Unit('hello world')
```

# Disadvantages

Since we're effectively continuously passing functions 
from one data unit to another, it makes it hard to 
access object methods of an object within a container.

Example: if we wanted to add just one value to a 
list within a container, we can't access append 
directly.

``` python
Unit([1,2,3]) | append(4) # can't do something like this

# Note that even list.append is an in-memory op 
# So this effectively returns None
Unit([1,2,3]) | (lambda x: x.append(4))
# => None
```

The Unit Functor does not store data between operations 
but rather stores the results of functions that operate 
on the data. _list.append_ doesn't return anything, 
but we can use functions like _concat_ to merge lists 
together.

``` python
Unit([[1,2,3],[4,5,6]]) | concat
# => Unit([1, 2, 3, 4, 5, 6])
```

# Notes

Check the Makefile for a quick shell launch option 
so you don't have to keep manually loading the file. 
There are shells for both normal Python and IPython.

Unit expressions will always return a Unit unless 
it has been told "True" at the end to signify that 
we want to extract the value from the Unit. You can 
also send a "False" to nullify the expression. 
(This means you could in practice nest Unit expressions 
so that one can act as an "If" conditional)

``` python
Unit(4) | succ | neg | True
# => -5

Unit(4) | False
# => None
```

# Credits and Such

If you like this, check out the following:

* [The Haskell Language](https://haskell.org/)
* [PyMonad](https://pypi.python.org/pypi/PyMonad/)

