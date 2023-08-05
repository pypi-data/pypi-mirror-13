#!/usr/bin/env python

"""
One package to unite the two files together
Instead of importing from separate packages, 
we do 'from Unit.All import *' to get 
both the Prelude and Unit class
"""

try:
    # Installed on the client import
    from .Functor import *
    from .Prelude import *
except Exception:
    # Local import from source project
    from Functor import *
    from Prelude import *
finally:
    # for when something isn't working
    pass

# end
