import pyparsing as pp
from bling import ast

expression = pp.Forward()

null = pp.Keyword('null').setParseAction(ast.Null)
boolean = pp.Keyword('true') | pp.Keyword('false')
boolean.setParseAction(ast.Boolean)

number = pp.Combine(
     pp.Optional('-') +
     ('0' | pp.Word('123456789', pp.nums)) +
     pp.Optional('.' + pp.Word(pp.nums)) +
     pp.Optional(pp.Word('eE', exact=1) + pp.Word(pp.nums + '+-', pp.nums)))
number.setParseAction(ast.Number)

nibble   = pp.Word(pp.hexnums, exact=1).setParseAction(lambda tokens: int(tokens[0] + tokens[0], 16))
byte     = pp.Word(pp.hexnums, exact=2).setParseAction(lambda tokens: int(tokens[0], 16))
hex_rgb  = pp.Suppress('#') + (byte * 3 | nibble * 3)
color    = hex_rgb.setParseAction(ast.Color)

literal = null | boolean | number | color

def identifier():
    return pp.Word(pp.alphas + "_")

reference = identifier().setParseAction(ast.Reference)

arguments = pp.Group(pp.Suppress('(') + pp.Optional(pp.delimitedList(expression)) + pp.Suppress(')'))
function_call = identifier() + arguments
function_call.setParseAction(ast.FunctionCall)

expression << literal | function_call | reference