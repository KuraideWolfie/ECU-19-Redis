# collect.py generates a list of field ids contained in ./bibliography-fields,
# and then prints this list (which is a set of the unique fields)

import sys, os

def __main__():
  fields = {}

  with open('./bibliography-fields.txt') as f:
    key = ""

    for ln in f.readlines():
      if '@' in ln:
        key = ln[1:].split("{")[0]
        fields[key] = []

      if '=' in ln:
        field = ln.split("=")[0].strip()
        if not field in fields[key]: fields[key].append(field)
  
  print(fields)

__main__()