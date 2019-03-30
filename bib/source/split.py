# DBLP format: https://dblp.uni-trier.de/faq/16154937

import sys
import os

def __main__(argc, argv):
  try:
    # If the filename wasn't specified, throw an exception
    if argc != 2: raise Exception()
    else:
      file = argv[1]
      fold = file[:file.rindex('/')+1]+'xml-bib/'

      # If the path given is not a file, then throw an exception
      if not os.path.isfile(file): raise Exception()
      else:
        # Create the directory to store the parsed bib if it doesn't exist
        if not os.path.exists(fold): os.mkdir(fold)

        with open(file, 'r') as fr:
          ent, ln, ent_cur, ent_cnt = [], fr.readline(), "", 0

          # Iterate through all of the lines in the document, splitting at </article> tags.
          # When groups of 10000 are discovered, write them to a separate file
          while not ln == "":
            found = False

            for typ in {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}:
              term = '</' + typ + '>'

              if term in ln:
                found = True
                ln = ln.split(term)
                ent_cur += ln[0] + term

                ent.append(ent_cur)
                ent_cur = ln[1]

                if len(ent) == 10000:
                  out = fold+str(ent_cnt)+".txt"
                  print("Writing file:", out)

                  with open(out, 'a') as fw:
                    for e in ent: fw.write(e+'\n')

                  ent.clear()
                  ent_cnt += 1

            if not found: ent_cur += ln
            ln = fr.readline()
        
        # Write the last of the entries to the disk
        out = fold+str(ent_cnt)+".txt"
        with open(out, 'a') as fw:
          for e in ent: fw.write(e+'\n')
  except Exception as e:
    print(e)
    print("Usage: python3 split.py <dblp file>")

__main__(len(sys.argv), sys.argv)