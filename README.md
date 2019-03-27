# ECU NSF Research Project
**Title**: ECU-19-Redis
<br />
**Author**: Matthew Morgan
<br />
**Supervisor**: Venkat Gudivada
<br />
**Date**: Started January 2019 _(updated 26 March 2019)_

## **Description**
This project is being developed as a research project for the NSF grant provided to East Carolina University. This project is overseen by Dr. Venkat Gudivada, and being worked upon by Matthew Morgan under his guidance. The project involves database management systems such as Redis, PostgreSQL, and utilities such as ElasticSearch.

## **Redis** and Boolean Retrieval
This task primarily centered around the creation of a 3-master, 3-worker Redis cluster, hosted graciously by ECU, and the generation of Redis documents using a subset of the Gutenberg corpora, after some pre-processing to remove extraneous data. Sample queries were run on this cluster, and tests performed to ensure data integrity on the failover of a master node.

**Software**:
+ Redis version 5.0.3, available at https://redis.io/download
    + _A 6-node Redis cluster - 3-worker, 3-master - was created using 6 machines with Redis configured for cluster usage on Linux OS_
+ Python v3.7.2
  + `sudo pip install redis-py-cluster`, providing the ability to interface with a redis cluster
    + This module uses the same functions as `sudo pip install redis`, but makes changes for a cluster
    + The API for redis-py is available at https://redis-py.readthedocs.io/en/latest/

## **Apache Lucene** and Sample Queries
### Subtask 01: Sample Queries on Gutenberg
This task primarily centered around the creation of an Apache Lucene program that could generate documents in field-value pairs, executed on a smaller subset of the Gutenberg Corpora formatted similarly to the Cranfield corpora. It was programmed using Java, and required the execution of a variety of queries, inclusive of, but not limited to boolean, term, and disjunction max queries. _(A program from the summer of 2018 was utilized to provide a start on this task.)_

**Software**:
+ Apache Lucene 7.3.0+, available at http://lucene.apache.org/
  + The `core` and `queryparser` libraries were utilized from the binary (JARs)
+ Java Development Kit 11 and Java Runtime Environment

### Subtask 02: Sample Queries on Bibliography
This task primarily centered around the modification of the aforementioned Lucene program, generating documents instead using bibliography fields from a provided document corpora. Before this could be done, cleaning of the bibliography was necessary using a script from GitHub.

**Software**:
+ Apache Lucene 7.3.0+, `core` and `queryparser` binaries
+ Java Development Kit 11, Java Runtime Environment
+ Python v3.7.2
  + `clean_bib` project on GitHub, available at https://github.com/ZacCat/clean_bib
    + `sudo pip install bibtexparser` is a dependency

## **Other Resources**
+ https://tartarus.org/martin/PorterStemmer/
  + Porter Stemmer algorithm, stemming tokens such as 'stealing' --> 'steal'
+ http://www.gutenberg.org/files/
  + Gutenberg Corpora file repository, where all corpora files are accessible

## Notes
If `sudo pip install` doesn't work for install, you may try `python3 -m pip install <package>` instead. To install the needed packages locally, simply append the `--user` tag to the installation command.