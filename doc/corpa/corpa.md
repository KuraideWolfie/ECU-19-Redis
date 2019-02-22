### Corpora Filtration
Prior to generating code to generate a boolean retrieval index, it was imperative to look at the Gutenberg corpora and remove unrequired data, and parse out other files that would be of no use. The original size of the corpora, when received, was over 50,000 documents in plaintext form. _Following is the series of steps I took to parse down the documents._

#### Gutenberg Licensure
I iterated through each of the documents and removed the Gutenberg licensure, exporting each license to its own file in a directory. (This licensure's beginning was targetted by searching for a line beginning with `*** END OF THIS PROJECT GUTENBERG EBOOK`.) Given that the corpora documents were also labelled as `<id>-<altver>.txt`, I segmented the corpora documents into segments of 1000, which was done by creating directories. (For example, directory `0-1` contains any TXT files with names of '0.txt' to '999.txt', as well as any alternate versions, such as '999-2.txt.') Documents were further segmented by language, leaving the following, sample file structure:

```
Gutenberg corpus root
+ 0-1
  + english
    + <file>
    + ...
    + <file>
  + ...
  + spanish
+ 0-2
+ ...
+ 58-59
```

#### Foreign Languages and Unbeneficial Data
Some corpora documents were filtered out after the segmentation for a variety of reasons, inclusive of being in foreign languages, and the documents containing content such as human genome and mathematical constant information - i.e. 1,000,000 digits of pi.

At the end of this stage, the number of files went from __50,000__+ --> __47,487__, and the overall size from __~20 GB__ --> __~17 GB__.

#### Duplicate IDs
Searching for unique identifiers for corpora documents led to the discovery that there were __~5,400__ replicated document IDs. These duplicate files were removed from the corpus, shrinking it another __2.25GB__.

### Augmented Corpora Notes
The final copy of the Gutenberg corpora, after all modifications, is contained in a series of folders under the `data` directory:
+ `cor`, or the corpora documents still viable for processing
+ `lic`, or the compressed licenses extracted from the corpa documents
+ `ign`, or ignored corpora documents, such as mathematical constants
+ `ign/lang`, or ignored corpora documents due to language
+ `ign/alt`, or ignored corpora documents due to being alternate copies<br/>
  _Alternate copies means encoding. Files with -8, -5, and -0 are utf-8, big-5, and ascii encoding respectively according to the gutenberg website_:
  https://www.gutenberg.org/files/

Corpora documents maintain certain metadata attributes from the original dataset, including the following lines at the top of each plaintext file:
+ `Title`: The title of the corpus document
+ `Author`: The authors of the document
+ `Release Date`: A date with ebook identifier, (`<date> [EBOOK #<id>]`), or just a date
+ `Languages`: Languages in the document
+ `Text`: The text itself

In regards to the following 'processing todo' points, there is a lot of inconsistency in the formatting of the Gutenberg corpa. As aforementioned, some files include an ebook identifier, but some may not; others, in turn, may format the date differently. Some have produced by lines, and some do not, and some do not maintain the original titles on the same line as the `Text` indicator above...

Processing **Todo**
+ 1118 contains a project notice before the start of the text
+ Multiple files include 'produced by' before start of the text
+ Some files contain notes from the editor about central themes
+ A few files contain transcriber notes about the file