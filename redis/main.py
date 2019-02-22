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
from ir import Token, tokenize, STOP_WORDS
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
    
    # for mst in master['files']:
    for i in range(0, master['count']):
      mst = master['files'][i]

      print(len(mst), 'files') # Debug print
      meta, tokens, stem = {}, {}, PorterStemmer()

      for f in mst:
        with open(f, 'r', encoding='utf-8') as fr:
          lines, pos, fid = fr.readlines(), 0, f[f.rfind('/')+1:f.rfind('.')].split('-')[0]
          dat = [lines[i][lines[i].index(':')+1:].strip() for i in range(0,4)]

          # Metadata for the document - name, auth, date
          meta[fid] = { 'name': dat[0], 'auth': dat[1], 'date': dat[2] }
          if '[' in meta[fid]['date']:
            date = meta[fid]['date']
            meta[fid]['date'] = date[:date.rindex('[')]

          print('  %5s : %s' % (fid, meta[fid]['name']))

          # Tokenized lines
          lines = [tokenize(line) for line in lines[5:]]
          lines = [line for line in lines if line]

          for line in lines:
            for word in line:
              pos += 1
              word = stem.stem(word, 0, len(word)-1)

              if not word in tokens:
                if word[0] in STOP_WORDS:
                  if word in STOP_WORDS[word[0]]: continue
                tokens[word] = Token(tok=word)

              tok = tokens[word]
              tok.add_doc(fid)
              tok.add_pos(fid, pos)
        
      # Push corpus data to the database
      print("Sending data to the server for", len(meta), "documents and", len(tokens), "tokens")

      for doc in meta:
        for tag in meta[doc]:
          # print(doc, tag, meta[doc][tag])
          r.hset('{'+rmaster[i]+'}doc:'+doc, tag, meta[doc][tag])
        
      for tok in tokens:
        r.sadd('{'+rmaster[i]+'}term:'+tok, *set(tokens[tok].docs))
        # for doc in tokens[tok].docs: r.lpush('pos:'+tok+'-'+doc, tokens[tok].pos[doc])
      # TODO Push raw documents here

    print()

  # ------------------------------------------------------------------------------------------------
  # Allow the user to type phrase and term queries
  done = False

  print("\nType '!stop' to exit querying")

  while not done:
    q = input("Query > ")

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
      res = r.sunion(['{%s}term:%s' % (mas,tok) for tok in tokenize(q) for mas in rmaster])

      print("There were", len(res), "hits")
      for doc in res:
        # Query all the master nodes for the document title
        for mst in rmaster:
          val = r.hget('{'+mst+'}doc:'+doc, 'name')
          if val == None: continue
          else:
            print('%7s' % (doc), ':', val)
    
    print()

__main__()