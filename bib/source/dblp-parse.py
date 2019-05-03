"""
  File:   dblp-parse.py
  Author: Matthew Morgan
  Date:   2 May 2019
  Description:
  This file parses the DBLP file, filtering out groups of 10000 entries and parsing
  them into a bibtex format.
"""

import sys, os, re

# records is a collection of all the records
# skip is the number of meta-data lines to skip
# rec is a list of all the lines of data for the current entry
# typ is the type of the current entry
records, skip = {}, 3
rec, typ = [], ''

PATH, file_count = '../dblp/', 0

def bibify(rec):
  """ bibify(rec) bibtex-ifies a single record generated by process(rec). It
      returns a string representing the record in bibtex form. """

  res = ("@%s{%s,\n" % (rec['type'].title(), rec['key']))

  for fld in rec:
    if not fld in ['key', 'type']:
      if fld == 'auth': res += ('%10s = "%s",\n' % (fld, ' and '.join(rec[fld])))
      else:             res += ('%10s = "%s",\n' % (fld, rec[fld]))

  res = res[:len(res)-2]+'\n}' # Clean up an excess comma

  return res

def process(rec):
  """ process(rec) processes a single record - that is, a collection of lines from
      the DBLP file that contain the XML fields and attributes for a single record
      in the massive file. It then resets values for a new record's values to be
      accrued for processing. """

  print(rec[0].split(' ')[0][1:], rec[0])
  global file_count, records

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

  	  if field == 'author':  record['auth'].append(val)
  	  elif field == 'pages': record['pages'] = '--'.join(val.split('-'))
  	  else:                  record[field] = val

  # Add the record to the collection. If the collection has breached a certain size, then
  # print those records to a file
  records[record['key']] = record

  if len(records) == 10000:
    with open(PATH+'entries/'+str(file_count)+'.bib', 'w+') as fw:
      fw.write(',\n\n'.join([bibify(records[r]) for r in records]))

    file_count += 1
    records = {}

  # Reset for a new record
  rec = []
  typ = ''

with open(PATH+'dblp.xml', 'r', encoding='utf-8') as fr:
  for ln in fr:
    ln = ln.strip()

    # Skip the first few lines, and also skip blank lines
    if skip > 0:
      skip -= 1
      continue
    if not ln: continue

    if typ == '': typ = ln.split(' ')[0][1:]
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

print('done')