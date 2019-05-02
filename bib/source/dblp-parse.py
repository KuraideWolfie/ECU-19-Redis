"""
  File:   dblp-parse.py
  Author: Matthew Morgan
  Date:   2 May 2019
  Description:
  This file parses the DBLP file, filtering out groups of 10000 entries and parsing
  them into a bibtex format.
"""

import sys
import re

# records is a collection of all the records
# skip is the number of meta-data lines to skip
# rec is a list of all the lines of data for the current entry
# typ is the type of the current entry
records, skip = {}, 3
rec, typ = [], ''

def process(rec):
  """ process(rec) processes a single record - that is, a collection of lines from
      the DBLP file that contain the XML fields and attributes for a single record
      in the massive file. It then resets values for a new record's values to be
      accrued for processing. """

  print(rec[0].split(' ')[0][1:], rec[0])

  # Generate record structure and metadata
  record = {}
  meta = rec[0][1:len(rec[0])-1].split(' ')
  date, key = meta[1].split('=')[1], meta[2].split('=')[1]

  record['type'] = meta[0]
  record['date'] = date[1:len(date)-1]
  record['key'] = key[1:len(key)-1]
  record['auth'] = []

  # Process all fields found for the record; some fields may require special
  # processing, such as authors or page numbers
  for ln in rec[1:]:
  	field, val = re.findall(r'.*</(.*)>$', ln), re.findall(r'<.*>(.*)</.*>', ln)

  	if len(val) > 0:
  	  field, val = field[0], val[0]

  	  if field == 'author':
  	  	record['auth'].append(val)
  	  if field == 'pages':
  	  	record['pages'] = '--'.join(val.split('-'))
  	  else:
  	  	record[field] = val

  # Reset for a new record
  records[record['key']] = record
  rec = []
  typ = ''

with open('../dblp/dblp.xml', 'r', encoding='utf-8') as fr:
  for ln in fr:
    if skip > 0:
      skip -= 1
      continue

  	# Remove linespace and skip blank lines
    ln = ln.strip()
    if not ln: continue

    if typ == '':
      # Get the type of the record
      typ = ln.split(' ')[0][1:]
    else:
      # Check if the record terminates in the line or is terminated by the line
      end = '</{}>'.format(typ)

      if ln == end:
      	process(rec)
      elif end in ln:
      	process(rec)
      	rec = [ ln[len(end):] ]

    rec.append(ln)

  # Process the last record
  process(rec)

print(len(records))

# meta = ln[1:len(ln)-1].split(' ')
# date, key = meta[1].split('=')[1], meta[2].split('=')[1]
# record['type'] = meta[0]
# record['date'] = date[1:len(date)-1]
# record['key'] = key[1:len(key)-1]

# print(record)