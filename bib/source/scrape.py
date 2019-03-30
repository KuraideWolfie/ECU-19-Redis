""" File:   scrape.py
    Author: Matthew Morgan
    Date:   29 March 2019

    Extensions:
    + pip install beautifulsoup4
    + pip install requests

    This small file can parse the download links from the bibliography website, accumulate them together,
    and then execute downloading to gather the various .bib and .gz files for usage in later tasks. Some
    entries will, undoubtedly, be replicas of others, since each subcollection entry may have more than 1
    download link listed.
"""

from time import sleep
import os
import sys
import re
import ftplib
from bs4 import BeautifulSoup
import requests

# soup(url) returns a BeautifulSoup object based on the given url's HTML
soup = lambda url : BeautifulSoup(getHtml(url), 'html.parser')

def getHtml(url):
  """ getHtml(url) retrieves the HTML of a webpage using requests. """

  req = requests.get(url)
  html = req.text
  return html

def __main__():
  # scrape()
  download()

def download():
  coll = {"bib": [], "gz": [], "html": [], "other": []}
  err = []

  # Accumulate files with a .bib, .gz, etc extension
  with open('../dat/INDEX.txt', 'r') as fr:
    for ln in fr.readlines():
      ln = ln.strip()
      end = [ln[-i-1:] for i in range(2,5)]

      if end[0].lower() == '.gz':     coll["gz"].append(ln)
      elif end[1].lower() == '.bib':  coll["bib"].append(ln)
      elif end[2].lower() == '.html': coll["html"].append(ln)
      else: coll["other"].append(ln)

  # Iterate through the BIB and GZ files, attempting to download them using ftp/http
  cur_file = 0

  for c in ['bib', 'gz']:
    for f in coll[c]:
      fname = "../dat/%05d %s.%s" % (cur_file, '-'.join(re.findall(r'[A-Za-z]+', f)), c)
      print(f)

      if os.path.isfile(fname):
        print("  --> SKIPPING: File exists already")
        cur_file += 1
        continue

      if f[:3] == 'ftp':
        try:
          # Establish an FTP connection and attempt to download the file
          url = f[6:]
          url_host = url[:url.index('/')]
          url_dir = url[len(url_host)+1:url.rindex('/')]
          print("  --> ", url_host, ", ", url_dir, sep='')

          ftp = ftplib.FTP(url_host, timeout=2)
          ftp.login()
          ftp.cwd(url_dir)
          ftp.retrbinary('RETR %s' % f[f.rindex('/')+1:], open(fname, 'wb').write)
          ftp.close()
          print("  --> ", fname, sep='')
        except KeyboardInterrupt:
          exit(0)
        except Exception as e:
          print("  --> ", e, sep='')
          err.append(f)
      elif f[:4] == 'http':
        # Open the HTTP protocol to attempt fetching the file
        try:
          print("  --> ", fname, sep='')
          resp = requests.get(f)

          if resp.ok and not resp.is_redirect:
            with open(fname, 'wb') as fwrite:
              fwrite.write(resp.content)
          else:
            print("  --> ", resp.status_code)

          resp.close()
        except KeyboardInterrupt:
          exit(0)
        except Exception as e:
          print("  --> ", e, sep='')
          err.append(f)
      
      sleep(1)
      cur_file += 1
  
  # Print files that had errors into ERRROR.TXT
  for e in err: print(e, file=open('../dat/ERROR.TXT', 'a'))


def scrape():
  # base_url is the base hyperlink for the website - where scraping begins
  # all_links is a dictionary of all the bib download links
  # FORBID is a list of links we forbid from counting in all_links since they're not important
  base_url = "https://liinwww.ira.uka.de/bibliography/"
  base = soup(base_url)
  all_links = {}
  FORBID = [
    "mailto:liinwwwa@ira.uka.de", "http://ortyl.org", "http://lucene.apache.org/java/1_4_3/queryparsersyntax.html",
    "http://liinwww.ira.uka.de/bibliography/Copyright.html", "http://liinwww.ira.uka.de/bibliography/Comments.html"
    "http://validator.w3.org/check?uri=referer", "http://jigsaw.w3.org/css-validator/check/referer", "index.html"
  ]

  # Iterate through the body's children to find the h3 with an a element with an id of 'linking',
  # and whose contents is the defined; then iterate backward to find the second ul, which contains
  # all the links to the necessary pages
  children = list(base.find('body').children)
  categories, links = None, []

  for i in range(0, len(children)):
    if str(children[i].name) == 'h3' and len(children[i].contents) == 1:
      if children[i].contents[0].get('id') == "linking" and children[i].contents[0].contents[0] == "Hyperlinks to bibliographies on specific topics":
        ul_enc = 0
        
        while ul_enc < 2:
          i -= 1
          if str(children[i].name) == 'ul': ul_enc += 1
        
        categories = children[i]
        break
  
  # Filter out each of the category URLs
  for cat in list(categories.children):
    if str(cat.name) == 'li':
      links.append(re.findall(r'href=\"([A-Za-z/.]*)\"', str(cat))[0])
  
  # Progress to each of the given pages, and iterate through each of the subcollection pages, taking
  # away the bibtex file
  for link in links:
    coll_base_url = base_url+link
    link_base = soup(coll_base_url)
    coll_base_url = coll_base_url[:coll_base_url.rindex('/')+1]

    # Subcollection information is stored as:
    # <table class="subcollectionindex">
    #   <tbody>
    #     <tr>
    #       <td class="refcount">
    #       <td class="subcoll"> <a href="LNK">
    #       <td>YEAR    
    for child in link_base.find('table', class_='subcollectionindex').find('tbody').contents:
      if str(child.name) == 'tr':
        col = child.find_all('td')
        subcoll = coll_base_url+col[1].find('a').get('href')
        
        # Subcollection download links are stored in a ul that has no class, with an h2 before it with an a element
        # inside with the value 'browse' as an id, and the text 'Browsing the bibliography'
        sub_base = soup(subcoll)
        print(subcoll)
        for a in sub_base.find_all('a'):
          down_link = a.get('href')

          # Only accept a link if it isn't null, isn't a bookmark with #, isn't local/forbidden, or contains a mailto
          # address. If there isn't a // in the link, then presumably the link is on the local server, and the category
          # URL should be substituted in to complete the link
          if not down_link == None:
            if not (down_link[0] == '#' or down_link[:2] == '..' or down_link in FORBID or 'mailto' in down_link):
              if not '//' in down_link:
                down_link = subcoll[:subcoll.rindex('/')+1] + down_link

              all_links[down_link] = 1 if not down_link in all_links else all_links[down_link]+1
              print('  ', down_link)

  # Sort the links by their frequency in descending, then write them to disk
  all_links_sorted = [lnk for (_, lnk) in sorted([(all_links[lnk], lnk) for lnk in all_links], reverse=True)]
  for lnk in all_links_sorted:
    print(lnk, file=open('../dat/INDEX.TXT', 'a'))

__main__()