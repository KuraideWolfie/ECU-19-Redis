"""
  File: query.py
  Author: Matthew Morgan
  Date: 22 February 2019

  Description:
  Query contains a class that represents a boolean query.
"""

import re

class Query:
  """ Query specifies a single query, with the following syntax:
      + `[]` is used for grouping subqueries (i.e. `light|[orange sky]`)
      + `|` specifies an or (i.e. `light blue|red`)
      + Whitespace specifies an and (i.e. `new moon`)
      + '!' specifies a not (I.e. `light !surpass`)

      The following are sample queries:
      + `blue dog ![red|purple]`: blue and dog and not red and not purple
  """

  def __init__(self, que):
    """ init(que) initializes a new query instance """
    self.data = []
    self.type = 'or'
    bits = parse(que)

    if len(bits) > 1:
      self.type = 'and'
    elif len(bits) == 1:
      # Try processing the query as an or query
      if '|' in bits[0]:
        self.type = 'or'
        bits = parse(bits[0], spl='|')
      
      # Try processing the query as a not query
      if len(bits) == 1 and '!' in bits[0]:
        self.type = 'not'
        bits = parse(bits[0], spl='!')

        if len(bits) > 1: raise Exception("Query syntax is invalid")
    
    # Query was empty
    if len(bits) == 0: raise Exception("Query cannot be empty")

    # Recursively build a query if it is comprised of many pieces
    for bit in bits:
      me = bit
      if self.type in ['and', 'or'] and bit[0] == '[' and bit[-1] == ']': me = bit[1:len(bit)-1]
      if self.type == 'not' and bit[0]+bit[1]+bit[-1] == '![]': me = bit[2:len(bit)-1]
      self.data.append(me if not special(me) else Query(me))

  def print(self):
    """ print() prints this Query instance as a string. """

    print('{', ' '+self.type.upper() if self.type == 'not' else '', sep='', end=' ')
    for i in range(0, len(self.data)):
      bit = self.data[i]
      if 'Query' in str(type(bit)): bit.print()
      else: print(bit, sep='', end=' ')
      if i < len(self.data)-1: print(self.type.upper(), sep='', end=' ')
    print('}', sep='', end=' ')
  
def special(val):
  """ special(val) returns whether any character in the given argument is
      reserved in the query syntax. """
  for c in val:
    if c in [' ', '|', '!', '[', ']']:
      return True
  return False

def parse(que, spl=' '):
  """ parse(que, spl=' ') parses a query, que, splitting it at any ungrouped
      appearance of the splitting character. If there is an invalid character
      in the query, then an exception is raised. """
    
  grp, pos, bit = 0, [0, 0], []

  for c in que.lower().strip():
    if not (c.isalpha() or special(c)):
      raise Exception("Query syntax is invalid")

    if c == '[': grp += 1
    elif c == ']': grp -= 1
    elif c == spl and grp == 0:
      bit.append(que[pos[0]:pos[1]])
      pos[0] = pos[1]+1
    pos[1] += 1

  if not pos[0] == pos[1]: bit.append(que[pos[0]:])
  return [b for b in bit if b]

# This code runs on execution of this file
# for q in ['', 'blue dog ![red|purple]', '[brown chair||stool]|knock  [blue|green|red light !!bulb] arm ![purple|yellow dog]']:
#   try:
#     Query(q).print()
#     print()
#   except Exception as e: print(e)