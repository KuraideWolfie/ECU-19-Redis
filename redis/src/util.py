"""
  File: util.py
  Author: Matthew Morgan
  Date: 23 January 2019

  Description:
  This file contains utility functions that assist in the processing of the
  Gutenberg corpora, such as gathering a list of files or prompting.
"""

import os
import sys

def fileList(start='./data/cor/0-1/'):
  """ fileList(start) generates a list of files in the provided starting directory

      Keyword arguments:
      start -- the starting directory (default './data/cor/0-1')

      Return: A list of files in the starting directory and its subdirectories
  """

  files = []

  for (folder, _, fName) in os.walk(start):
    for name in fName: files.append(os.path.join(folder, name).replace('\\', '/'))
  
  return files

def confirm(prompt='y/n'):
  """ confirm(prompt) will prompt the user to enter yes or no until they enter one or the other
      
      Keyword arguments:
      prompt -- The prompt text to be shown to the user

      Return: True if the user enters y or yes, or False if they enter n or no
  """

  while True:
    inp = input(prompt+' > ').lower()
    if inp == 'y' or inp == 'yes': return True
    if inp == 'n' or inp == 'no': return False

def flushprint(msg, end='\n'):
  """ flushprint(msg, end='\n') writes the given message then flushes standard output

      Keyword arguments:
      msg -- The message to be printed
      end -- The ending character to be placed after the message
  """

  print(msg, end=end)
  sys.stdout.flush()