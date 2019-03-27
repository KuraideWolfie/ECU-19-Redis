# collect.py generates a list of field ids contained in ./bibliography-fields,
# and then prints this list (which is a set of the unique fields)

import sys, os

def __main__():
  fields = []

  with open('./bibliography-fields.txt') as f:
    for ln in f.readlines():
      if '=' in ln:
        field = ln.split('=')[0].strip()
        if not field in fields: fields.append(field)
  
  print(sorted(fields))

__main__()