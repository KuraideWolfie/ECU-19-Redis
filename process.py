"""
  File: process.py
  Author: Matthew Morgan
  Date: 20 February 2019

  Description:
  Process is a simple program that performs automated processing on corpora documents.
"""

from redis.util import fileList, confirm
import os

files = fileList(start="./data/cor/")

""" Move files from 'english' and 'en' directories to their parent directories """
# for f in files:
#   if 'english' in f or 'en' in f:
#     nm = f[:f.rfind('/')]
#     nm = nm[:nm.rfind('/')+1]
#     print(nm+f[f.rfind('/')+1:])
#     os.rename(f, nm+f[f.rfind('/')+1:])

def getid(f): return f[f.rfind('/')+1 : len(f)-4]
def newname(f):
  nm = f
  for _ in range(0, 3): nm = nm[nm.find('/')+1:]
  return f[:len(f)-len(nm)] + ('alt/' if not 'alt' in f else '') + nm

""" Process the document IDs, locating duplicates and showing content from these files """
# fids = { }

# Generate the dictionary of unique fids, where each entry is a list of filenames
# that contain that fid
# for (fid, path) in [(getid(f), f) for f in files]:
#   ent = fid if not '-' in fid else fid[:fid.rfind('-')]
#   if not ent in fids: fids[ent] = [ path ]
#   else: fids[ent].append(path)

# for fid in [f for f in fids if len(fids[f]) > 1]: # FIDs with > 1 file with that fid in it
#   for f in fids[fid][::-1][1:]:
#     new = newname(f)
#     fol = new[:new.rfind('/')]

#     if not os.path.exists(fol): os.makedirs(fol)
#     os.rename(f, new)
  
# print(len(fids), len(files))

# ./data/cor/28-29/28889-0.txt