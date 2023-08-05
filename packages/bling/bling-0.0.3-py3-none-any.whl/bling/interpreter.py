from .ast import *

# library = LibrarySymbolTable()
# state = SymbolTable(library)

# On state change, get delta - parse as JSON into ordered dictionary
# current = state
# For each key:
#   switch(type):
#       null: unset key in current namespace
#       boolean: put BooleanConstant in current namespace
#       STRING: evaluate and put result in current namespace
#       NUMBER: put NumberConstant in current namespace
#       ARRAY: evaluate each (strings ONLY) and create a Texture, put in current namespace
#       OBJECT: get or create child namespace, set to current and recurse.

# Every tick, for current sequence
# t = current_time (0.0 .. 1.0)
# for led in range(61):
#    x = led / 60.0
#    state[current_sequence].evaluate(x=x, t=t)

class BlingParser(object):
    def parse_expression(self, expression):
        pass

class Namespace(SymbolTable):
    def evaluate(context):
        pass