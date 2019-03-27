clear

mkdir ../out

javac -cp ".:../lib/lucene-queryparser-7.3.0.jar:../lib/lucene-core-7.3.0.jar" Lucene.java -d ../out

jar -cvfm ../Lucene.jar ../manifest.txt -C ../out .

# java -jar Lucene.jar ./cranform/ -index ./index/ -trace

rm -d -r ../out