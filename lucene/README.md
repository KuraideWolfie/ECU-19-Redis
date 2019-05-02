# Apache Lucene, Gutenberg Corpora, and Bibtex
## Corpus Files
Contained in the 'corpus' directory are two subdirectories: `cranform`, and `original`. It also contains a file, `bibliography.txt`, that contains bibtex-formatted entries. The original directory contains unmodified versions of a few of the Gutenberg Corpora's documents, and cranform contained modified variants that conform to this standard:

```
.T
Title of the document
.A
Author of the document
.B
Bibliography
.W
Content of the Document Itself
```

These files conform to this standard because of how one of the source code variants operates, as it requires these fields to properly construct Lucene documents. See below for the different source variants.

**Licenses for these libraries are included in the `/lib/` directory!**

## Source Variants
There are two major variants of the Apache Lucene source code (one adapted from the original, which was constructed last summer): Gutenberg, and Bibliography. Each of these variants requires the Apache Lucene libraries, which are included in the `lib` directory. There is another library also included, detailed below.

### Gutenberg
The gutenberg variant of the Lucene source is the original from last summer. It required the gutenberg corpora be reconfigured to fit the Cranfield corpus specifications, detailed above. It uses this format to generate the proper fields for a Lucene Document, which is field-value pairs that are indexed for searching. It requires no libraries other than the `Apache Lucene` core and queryparser libraries (by preference, version 7.3.0, since that was the development version).

**Execution**:
```
javac -cp ".:../lib/lucene-queryparser-7.3.0.jar:../lib/lucene-core-7.3.0.jar" Lucene.java -d ../out
jar -cvfm ../Lucene.jar ../manifest.txt -C ../out .
java -jar Lucene.jar ./cranform/ -index ./index/ -trace
```

### Bibliography
The bibliography variant is modified to no longer require the Cranfield specification, but to parse bibtex-formatted entries. As such, it requires an external library - `JBibTex` - for parsing the bibliography file included in the corpus directory alongside the original Lucene libraries.

```
javac -cp ".:../lib/lucene-queryparser-7.3.0.jar:../lib/lucene-core-7.3.0.jar:../lib/jbibtex-1.0.17.jar" Lucene.java -d ../out
jar -cvfm ../Lucene.jar ../manifest.txt -C ../out .
java -jar Lucene.jar ../corpus/bibliography.txt -index ./bibliography/index/ -regen
```