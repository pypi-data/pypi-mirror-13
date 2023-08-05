import colour
import decimal

# Does not belong here.
class NestedDict(dict):
    """A dictionary that defers missing keys to a parent dictionary."""
    def __init__(self, parent=None):
        self.parent = dict() if parent is None else parent
        
    def __missing__(self, key):
        return self.parent[key]

class Node(object):
    """The base class for nodes in a Bling syntax tree."""
    def __init__(self, string='', location=0, tokens=[]):
        self.string = string
        self.location = location
        self.set_fields(*tokens)
        
    def set_fields(self, *tokens):
        pass
        
    def __str__(self):
        return self.string

class Literal(Node):
    def evaluate(self, context):
        return self.value
        
class Null(Literal):
    def set_fields(self, keyword):
        self.value = None
        
class Boolean(Literal):
    def set_fields(self, keyword):
        self.value = True if keyword == "true" else False
        
class Number(Literal):
    def set_fields(self, number):
        self.value = decimal.Decimal(number)

class Color(Literal):    
    def set_fields(self, r, g, b):
        rgb = (r / 255.0, g / 255.0, b / 255.0)
        self.value = colour.Color(rgb=rgb)

class Reference(Node):
    def set_fields(self, name):
        self.name = name
        
    def evaluate(self, context):
        referenced = context[self.name]
        return referenced.evaluate(context)
        
class FunctionCall(Node):
    def set_fields(self, name, arguments):
        self.name = name
        self.arguments = arguments
        
    def evaluate(self, context):
        return "TODO"