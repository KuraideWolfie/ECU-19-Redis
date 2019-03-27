/*
 * File:    Heaper.java
 * Author:  Matthew Morgan
 * Description:
 * This file contains functionality for gathering data for Heaps' Law.
 *
 * A heaper is basically a couple of lists - one for the points for the docs,
 * and one for the unique terms of the docs. All interaction with these points
 * is done via the few functions made available. (The Duet class is used, with
 * the first data variable being the total number of terms encounterd, and the
 * second the total number of unique terms.)
 */

// Import statements
import java.util.ArrayList;
import java.io.File;
import java.io.IOException;
import java.io.FileWriter;
import java.io.BufferedWriter;

public class Heaper {
  class Duet<A,B> {
    public A dataA;
    public B dataB;
    public Duet(A a, B b) { dataA = a; dataB = b; }
    public Duet() { dataA = null; dataB = null; }
  }

  // points is a list of duet lists, where each entry is a document's data pts
  // unique is a list of unique tokens in the documents
  private ArrayList<ArrayList<Duet<Integer,Integer>>> points;
  private ArrayList<ArrayList<String>> unique;

  public Heaper() {
    points = new ArrayList<ArrayList<Duet<Integer,Integer>>>();
    unique = new ArrayList<ArrayList<String>>();
  }

  /** Returns the number of documents in the heaper
    * @return The number of docs in the heaper presently */
  public int docs() { return points.size(); }

  /** Adds a document to the heaper. */
  public void addDoc() {
    points.add(new ArrayList<Duet<Integer,Integer>>());
    unique.add(new ArrayList<String>());
  }

  /** Adds a point to the list of data points in the heaper.
    * @param doc The document to add the point to */
  public void addPoint(int doc) {
    points.get(doc).add(
      new Duet<Integer,Integer>(points.get(doc).size()+1, unique.get(doc).size())
    );
  }

  /** Adds a term to a document if it doesn't already have the term
    * @param doc The document to add the term to
    * @param tok The term to be added */
  public void docAddTerm(int doc, String tok) {
    if (!unique.get(doc).contains(tok))
      unique.get(doc).add(tok);
  }

  /** Saves the data in the heaper to the disk in the specified directory.
    * @param dir The directory to store heap files in */
  public void save(String dir) {
    // w is used for writing information to files
    // f is used for checking the existence of directories
    BufferedWriter w;
    File f = new File(dir);

    if (!f.exists()) { f.mkdirs(); }

    /* Try to write all the points for each corpus entry into its own file in
     * the directory specified by the user. The files are CSV format. */
    try {
      for(int i=0; i<points.size(); i++) {
        w = new BufferedWriter(new FileWriter(dir+"heap-"+i+".csv"));

        w.write("ttl,unique\n");
        for(Duet<Integer,Integer> pt : points.get(i))
          w.write(pt.dataA+","+pt.dataB+"\n");
        w.write("\n");

        w.close();
      }
    }
    catch(IOException e) {
      System.out.println("ERR: Error during heap data save!");
      System.exit(1);
    }
  }
}