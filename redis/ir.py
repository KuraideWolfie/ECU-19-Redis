"""
  File: ir.py
  Author: Matthew Morgan
  Date: 6 February 2019

  Description:
  IR contains a definition of a Token class, and other useful functions to tokenization or other
  IR-related functions.
"""

class Token:
  """ A Token is a representation of a single word (stemmed or otherwise) in a document corpora,
      storing a positional and boolean retrieval indices.

      Variables:
      + token -- The string representation of this token
      + docs -- A list of documents the token appears in
      + pos -- A dictionary of positional indices for the token in its documents

      Functions:
      + `add_doc(doc)`      Add a document to this token's appearances
      + `add_pos(doc, pos)` Add a positional appearance to a document
      + `num_doc()`         Get the number of documents this token appears in
      + `num_pos(doc)`      Get the number of positions in the document
      + `print_docs()`      Print the document IDs of the token
      + `print_pos()`       Print positional indices for the token
  """

  def __init__(self, tok=''):
    """ __init__(tok) creates a new Token instance
       
       Keyword arguments:
       token -- The word/token this instance represents

       Return: A new Token instance
    """
    self.token = tok
    self.docs = []
    self.pos = {}
  
  def add_doc(self, doc):
    """ add_doc(doc) adds a new document to this token's list of document appearances
        
        Keyword arguments:
        doc -- The document - a string or integer

        Return: True if the document was added, or false if not
    """
    if not doc in self.docs:
      self.docs.append(doc)
      return True
    else:
      return False
  
  def add_pos(self, doc, pos):
    """ add_pos(doc, pos) adds a positional occurence to the specified document in this token
        
        Keyword arguments:
        doc -- The document this positional occurence applies to
        pos -- The position in the document of the token's appearance
    """
    if not doc in self.pos: self.pos[doc] = [ pos ]
    else: self.pos[doc].append(pos)
  
  def num_doc(self): return len(self.docs)
  def num_pos(self, doc): return len(self.pos[doc]) if doc in self.pos else 0

  def print_docs(self): print(self.token, self.docs)
  def print_pos(self):
    for doc in self.pos: print(self.token, doc, self.pos[doc])

# --------------------------------------------------------------------------------------------------

def tokenize(line):
  """ tokenize(line) parses a line of text, isolating all words using the following parse rules:
      + Lowercase the line, if it isn't already lowercase
      + Any character than 0-9, a-z, and spaces are removed
      + If there is a sequence of 2 hyphens, they are replaced by a space; single hyphens are left alone
    
      Keyword arguments:
      line -- the line of text to be parsed

      Return: The list of parsed tokens
  """

  pc, par, line = None, "", line.lower()

  for c in line:
    if (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') or c in ' ': par += c
    if (not pc == None) and (pc == '-' and c == '-'): par = par[:len(par)-2] + ' '
    pc = c
  
  return [w for w in par.split(' ') if len(w) > 0]