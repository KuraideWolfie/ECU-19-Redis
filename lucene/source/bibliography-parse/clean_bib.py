import datetime
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import *

import sys, getopt

unwanted = ['interhash', 'intrahash', 'timestamp', 'biburl', 'added-at']
wanted = ['ENTRYTYPE', 'ID',
          'abstract', 'address', 'author', 'booktitle', 'chapter', 'edition',
          'editor', 'howpublished', 'institution', 'isbn', 'journal', 'month',
          'note', 'number', 'organization', 'pages', 'publisher', 'school',
          'series', 'title', 'volume', 'year']

# Let's define a function to customize our entries.
# It takes a record and return this record.
def customizations(record):
    """Use some functions delivered by the library
    :param record: a record
    :returns: -- customized record
    """
    record = type(record)
    record = page_double_hyphen(record)
    record = convert_to_unicode(record)
    ## delete the following keys.
    # for val in unwanted:
    #     record.pop(val, None)
    for val in list(record.keys()):
        if not (val in wanted): record.pop(val, None)
    # for v in [k for k in record.keys() if not k in wanted]:
    #     record.pop(v, None)
    return record


def main(argv):
    input_b = ''
    output_b = ''
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print ('clean_bib.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('clean_bib.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_b = arg
        elif opt in ("-o", "--ofile"):
            output_b = arg
            
    print ('Input file is "', input_b)
    print ('Output file is "', output_b)

    if(output_b == ''):
        output_b = input_b
        
    now = datetime.datetime.now()
    print("{0} Cleaning duff bib records from {1} into {2}".format(now, input_b, output_b))

    bib_database = None
    with open(input_b) as bibtex_file:
        parser = BibTexParser()
        parser.customization = customizations
        parser.ignore_nonstandard_types = False
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    if bib_database :
        now = datetime.datetime.now()
        success = "{0} Loaded {1} found {2} entries".format(now, input_b, len(bib_database.entries))
        print(success)
    else :
        now = datetime.datetime.now()
        errs = "{0} Failed to read {1}".format(now, input_b)
        print(errs)
        sys.exit(errs)

    bibtex_str = None
    if bib_database:
        writer = BibTexWriter()
        writer.order_entries_by = ('author', 'year', 'type')
        bibtex_str = bibtexparser.dumps(bib_database, writer)
        #print(str(bibtex_str))
        with open(output_b, "w") as text_file:
            print(bibtex_str, file=text_file)

    if bibtex_str:
        now = datetime.datetime.now()
        success = "{0} Wrote to {1} with len {2}".format(now, output_b, len(bibtex_str))
        print(success)
    else:
        now = datetime.datetime.now()
        errs = "{0} Failed to write {1}".format(now, output_b)
        print(errs)
        sys.exit(errs)
        
if __name__ == "__main__":
    main(sys.argv[1:])