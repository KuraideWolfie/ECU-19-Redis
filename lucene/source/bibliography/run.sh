clear

mkdir ../out

# javac -cp ".:../lib/lucene-queryparser-7.3.0.jar:../lib/lucene-core-7.3.0.jar" Lucene.java -d ../out
javac -cp ".:../lib/lucene-queryparser-7.3.0.jar:../lib/lucene-core-7.3.0.jar:../lib/jbibtex-1.0.17.jar" Lucene.java -d ../out

jar -cvfm ../Lucene.jar ../manifest.txt -C ../out .

read -p "Compilation Ends Here"
clear
cd ..

# java -jar Lucene.jar ./cranform/ -index ./index/ -trace

# java -jar Lucene.jar ../corpus/bibliography.txt -index ./index -trace -regen
java -jar Lucene.jar ../corpus/bibliography.txt -index ./bibliography/index/ -regen
rm -d -r out