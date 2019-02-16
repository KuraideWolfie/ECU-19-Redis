# Introduction
**Title**: ECU-19-Redis
<br />
**Author**: Matthew Morgan
<br />
**Supervisor**: Venkat Gudivada
<br />
**Date**: Started January 2019 _(updated 15 February 2019)_

### **Description**
This project is being developed as a research project for the NSF grant provided to East Carolina University. This project is overseen by Dr. Venkat Gudivada, and being worked upon by Matthew Morgan under his guidance.

# **Requirements**
**Language(s)**: Python v3.7.2

### **Python Extensions**
+ `sudo pip install redis-py-cluster`
  + Module that provides the ability to interface with a Redis cluster
  + This module uses the same functions as `sudo pip install redis`, exempt that it makes some changes for working with clusters
    + The API for redis-py is available at https://redis-py.readthedocs.io/en/latest/

### **Other Resources**
+ https://tartarus.org/martin/PorterStemmer/
  + Porter Stemmer algorithm, stemming tokens such as 'stealing' --> 'steal'
+ http://www.gutenberg.org/files/
  + Gutenberg Corpora file repository, where all corpora files are accessible