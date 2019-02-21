"""
  File: main.py
  Author: Matthew Morgan
  Date: 23 January 2019

  Description:
  This program reads in a significant amount of data from the Gutenberg corpora, processing the
  title, author, dates, and content of each document to generate a postings index for each unique
  term in the corpora.
"""

from rediscluster import StrictRedisCluster
from stem import PorterStemmer
from ir import Token, tokenize
from util import confirm, fileList
import sys

# rhost, rport, and rpass are login credentials for the cluster, where rhost is the first three
# octets of the server's IP. (A list comprehension will build the list of nodes)
rhost, rport, rpass = '150.216.79.', 6379, '1997mnmRedisStudies2019'

"""
    rmaster is a list of keys that, when enclosed in {}, will hash to a slot on the corresponding
    master as the index the key is contained in. For example, "3" will evaluate to 1584, and thus
    be sent to the first master node.

    The documents that will be sent to a corresponding master will be based on modulous as to
    provide a semi-even distribution; that is, document 0 goes to node 0, 1->1, and 2->2, but then
    document 3 goes back to node 0, 4->1, 5->2, etc. (This is NOT the same as using the fid's of
    the corpora; the indices of the files as they appear in the list are what will be used)

    The current list evaluates to slots [1584, 5649, 13907] respectively.
"""
rmaster = ["3", "2", "0"]

def __main__():
  global rhost, rport, rpass, rmaster

  # ------------------------------------------------------------------------------------------------
  # Connect to the Redis database, or terminate if the connection fails
  print("Connecting to server...", sep="")

  try:
    r = StrictRedisCluster(startup_nodes=[{"host": rhost+str(n), "port": rport} for n in range(30, 36)],
      decode_responses=True, password=rpass)
  except Exception:
    print("Error connecting to database...")
    sys.exit(1)
  
  print("Connection successful")

  # Prompt to clear the database
  nodes = r.dbsize()
  for node in nodes:
    if nodes[node] > 0:
      if confirm("Clear the database? (y/n)"):
        r.flushall()
      break

  # ------------------------------------------------------------------------------------------------
  if confirm("Load corpus data? (y/n)"):
    # master contains a list of files for each master node and the number of master nodes
    # files is a list of ALL files in the corpus directory (specifiable by use_dir)
    master = { "files": [], "count": len(rmaster) }
    files, use_dir = [], ''

    # The user inputs the corpus directory they want, then we make empty file lists for each of
    # the master nodes. We then fill those lists using a round-robin methodology involving modulous
    use_dir = input("Input corpus directory (blank for none) > ").strip()
    files = fileList('./data/cor/0-1/' if use_dir == "" else use_dir)

    for i in range(0, master['count']): master['files'].append([])
    for i in range(0, len(files)):
      master['files'][i % master['count']].append(files[i])
      # print('Master', i % master['count'], 'has file', files[i]) # Debug print
    
    for mst in master['files']:
      print(len(mst), 'files') # Debug print

      for f in mst:
        print(f)
        # TODO Generate meta-data, BR, and positional and push to Redis here
      # TODO Push raw documents here

    # tDic stores the metadata for the documents
    # tokens is a dictionary of the tokens discovered in the documents
    # stem is the Porter Stemmer class, instantiated
    # tDic, tokens, stem = {}, {}, PorterStemmer()

    # for i in range(0, len(files)):
    #   f = files[i]

      # with open(f, 'r', encoding='utf-8') as fRead:
      #   lines, pos = fRead.readlines(), 0

      #   meta = {
      #     "name": lines[0][lines[0].index(':')+1:].strip(),
      #     "auth": lines[1][lines[1].index(':')+1:].strip(),
      #     "date": lines[2][lines[2].index(':')+1:].strip(),
      #     "lang": lines[3][lines[3].index(':')+1:].strip().lower()
      #   }

      #   if '[' in meta['date']: meta['date'] = meta['date'][:meta['date'].rindex('[')]
      #   tDic[f] = meta

      #   # Tokenize lines and remove those that are empty after tokenization
      #   lines = [tokenize(line) for line in lines[5:]]
      #   lines = [line for line in lines if line]

      #   for line in lines:
      #     for word in line:
      #       pos += 1
      #       word = stem.stem(word, 0, len(word)-1)
      #       if not word in tokens: tokens[word] = Token(tok=word)

      #       tok = tokens[word]
      #       tok.add_doc(f)      # Boolean retrieval
      #       tok.add_pos(f, pos) # Positional index
      
      # print(master, ':', tDic[f]['name'])
    print()

    # ----------------------------------------------------------------------------------------------
    # if confirm("Load data into database? (y/n)"):
      # Add the data to the database
      # print("Copying document data to the database... (", len(tDic), " documents)", sep='')
      # for doc in tDic:
      #   r.hset('doc:'+doc, 'name', tDic[doc]['name'])
      #   r.hset('doc:'+doc, 'auth', tDic[doc]['auth'])
      #   r.hset('doc:'+doc, 'date', tDic[doc]['date'])
    
      # print("Copying word data to the database... (", len(tokens), " tokens)", sep='')
      # for tok in tokens:
      #   r.sadd('term:'+tok, *set(tokens[tok].docs))
      #   for doc in tokens[tok].docs: r.lpush('post:'+tok+'-'+doc, tokens[tok].pos[doc]) # TODO Connection error

  # ------------------------------------------------------------------------------------------------
  # Allow the user to type phrase and term queries
  done = False

  print("\nType '!stop' to exit querying")

  while not done:
    q, search = input("Query > "), []

    if q == '!stop': done = True
    elif q == '!sys':
      keys, info, rep = r.dbsize(), r.info(section='memory'), r.info(section='replication')

      print('Database Master Nodes')
      for node in [k for k in keys if rep[k]['role'] == 'master']:
        print('  ', node, ' -> ', keys[node], ' keys', sep='')
        print('    Memory: (Cur\\Ttl -> %s \\ %s), (RSS\\LUA -> %s \\ %s)' %
          (info[node]['used_memory_human'], info[node]['total_system_memory_human'],
           info[node]['used_memory_rss_human'], info[node]['used_memory_lua_human']))
        print('    Workers:', rep[node]['connected_slaves'])
    else:
      for term in tokenize(q): search.append('term:'+PorterStemmer().stem(term, 0, len(term)-1))
      res = r.sinter(search)

      print("There were", len(res), "hits")
      for doc in res:
        print('%7s' % (doc), ':', r.hget('doc:'+doc, 'name'))
    
    print()

__main__()