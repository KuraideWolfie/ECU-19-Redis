/*
 * File:    Lucene.java
 * Author:  Matthew Morgan
 * Date:    24 May 2018   : Initial
 *          18 March 2019 : Added Lucene Query Examples
 * Description:
 * This class provides a basic implementation of the Apache Lucene 7.3.0 API.
 * It was primarily made to demonstrate Lucene's capabilities on a basic level,
 * but also provide:
 * - cf, tf, idf, and df information for corpus tokens
 * - Heaps' Law coordinate data for graphing (verification of Heaps' Law)
 *
 * For the purposes of this project, a single Document will contain these
 * fields (following Cranfield specification):
 * - id:        A unique numerical identifier
 * - title:     The title of the document (.T)
 * - author:    The author of the document (.A)
 * - bib:       The bibliography of the document (.B)
 * - content:   The content of the document itself (.W)
 *
 * To parse the documents with these fields, the following format (that of the
 * Cranfield Collection) is assumed to be followed:
 * .T
 * Title of the document
 * .A
 * Author of the document
 * .B
 * Bibliography of the document
 * .W
 * Content of the document, either on one line or numerous lines
 *
 * The following are special commands recognized by the system during querying.
 * They should be prefixed by '!' for them to work appropriately. If you wish
 * to search using '!' as the first character, escape it with '!' behind it
 * (such as !!search).
 * - stop:    Stops the querying interface. ALWAYS use this to stop querying
 *   usage:   !stop
 * - term:    Allows printing of term tf, df, idf, and cf information
 *   usage:   !term <TERM|!all|!n> [fname]
 * - explain: Explains a query against a document ID
 *   usage:   !explain <doc> <query>
 *
 * Bucketlist:
 * - Modify the number of results fetched by lucene ("!sys hits n")
 * - Allow redirection of queries from a file
 * - The explanation command doesn't work correctly if only 2 terms are specified; a try-catch
 *   may be required to catch if the length of the array, after splitting the query at spaces,
 *   is of length 2
 * - Create query history for explanations
 */

// Import statements
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.Term;
import org.apache.lucene.index.TermsEnum;
import org.apache.lucene.index.PostingsEnum;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.document.*;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.*;
import org.apache.lucene.util.BytesRef;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.simple.SimpleQueryParser;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Scanner;
import java.util.Collections;

public class Lucene {
    /* LToken is a simple class, provided to allow token data to be easily
     * stored and iterated through for printing by the !term special command.
     * It stores all the frequencies, and provides a simple way of sorting
     * the set of tokens by their collection frequency. */
    static class LToken implements Comparable<LToken> {
        // tf, cf, and df are the term, collection, and document frequencies
        // idf is the inverted document frequency (log(numDocs/docFreq))
        // term is the text representing the term
        // termObj is the Term object representing the LToken
        long[] tf;  int df;
        long cf;    double idf;
        String term; Term termObj;

        /** Public constructor that instantiates a blank LToken
          * @param docs The number of documents in the collection */
        public LToken(int docs, String tok) {
            tf = new long[docs];
            for(int i=0; i<docs; i++) { tf[i] = 0; }
            df = -1; cf = -1; idf = -1;
            term = tok;
            termObj = new Term("content", tok);
        }

        /** Converts this token's information into a string.
          * @return The token's information, as a string */
        public String info() {
            String tmp = String.format("%20s %5d %6d %10f", term, df, cf, idf);
            for(int i=0; i<tf.length; i++)
                tmp = String.format("%s %5d", tmp, tf[i]);
            return tmp;
        }

        @Override
        public int compareTo(LToken other) {
            return Long.compare(cf, other.cf);
        }
    }

    // TOP_RESULT_COUNT is the number of results to be fetched by the searcher
    public static final int TOP_RESULT_COUNT = 100;

    /* PROG_TRACE prints some simple, preliminary tracing statements to ensure
     * proper program execution */
    // corpus is the location of the corpus to be read on the disk
    // corpus_list is a list of all the entries in the corpus
    // index specifies where the location of the index should be
    // heap specifies where Heaps' Law data, if desired, should be stored
    // om is the openmode for the index, and is CREATE_OR_APPEND by default
    /* parserType specifies which parser to use (0 for QueryParser, 1 for
     * SimpleQueryParser) */
    /* LTL is a list of LToken objects that would be generated whenever the user
     * runs the '!term' command. It's kept in a variable to prevent duplicate
     * generations of the list */
    public static boolean PROG_TRACE = false;
    static String corpus = "", index = "./index/", heap = "";
    static ArrayList<String> corpus_list = new ArrayList<>();
    static ArrayList<LToken> LTL = null;
    static Heaper heaper = null;
    static IndexWriterConfig.OpenMode om = IndexWriterConfig.OpenMode.CREATE_OR_APPEND;
    static byte parserType = 0;

    /* analyzer is a standardanalyzer, and will filter stop words, perform
     * lowercasing, and apply other tokenization procedures to tokens. */
    /* directory is a new FSDirectory that will point to the folder 'index'. */
    /* iWriteConfig will provide configuration information for the IndexWriter
     * iWrite. iWrite will be used to write documents to the filesystem. */
    /* reader allows the directory to be read by the IndexSearcher. */
    /* iSearch will perform all searches on the index corresponding to the
     * queries entered by the user. */
    /* qParse will be responsible for parsing user queries, allowing them to
     * execute searches on the index and get results. */ 
    /* query is a temporary storage variable for storing the user's most recent
     * executed query on the indexed corpus. */
    /* result is a variable for storing the results of user queries. */ 
    static Analyzer analyzer;
    static Directory directory;
    static IndexWriterConfig iWriteConfig;
    static IndexWriter iWrite;
    static DirectoryReader reader;
    static IndexSearcher iSearch;
    static QueryParser qParse = null;
    static SimpleQueryParser sqParse = null;
    static Query query;
    static ScoreDoc[] result;

    public static void main(String[] args) {
        argumentCheck(args);
        if (PROG_TRACE) {
            printTrace("Cor|Ind|Hep: '"+corpus+"', '"+index+"', '"+heap+"'");
            printTrace("Parser     : "+parserType);
        }

        try {
            /* Create the analyzer and open an FSDirectory implementation. The
			 * Analyzer is instantiated with a blank set of stop words */
            analyzer = new StandardAnalyzer(org.apache.lucene.analysis.CharArraySet.EMPTY_SET);
            directory = FSDirectory.open((new File(index)).toPath());

            /* Process the corpus, generating a list of filenames, opening each
             * in turn and indexing their properties using the IndexWriter. The
             * writer is closed after Documents have been appended. (Documents
             * are added after IndexWriterConfig has been setup and passed to
             * IndexWriter as a constructor parameter)
             *
             * The corpus may not be processed if the index directory exists.
             * This is meant to save CPU time if the corpus has been processed
             * once before (and prevent duplicated documents in the index) */
            if (!DirectoryReader.indexExists(directory) && om != IndexWriterConfig.OpenMode.CREATE) {
                iWriteConfig = new IndexWriterConfig(analyzer);
                iWriteConfig.setOpenMode(om);
                iWrite = new IndexWriter(directory, iWriteConfig);
                iWrite.addDocuments(corpusProcess());
                iWrite.commit();
                iWrite.close();
            }
            else if (PROG_TRACE) { printTrace("Skipping corpus processing!"); }

            /* Instantiate a DirectoryReader, pass it to an IndexSearcher that
             * is also instantiated, and then instantiate a QueryParser */
            reader = DirectoryReader.open(directory);
            iSearch = new IndexSearcher(reader);

            switch(parserType) {
                case 0: qParse = new QueryParser("content", analyzer); break;
                case 1: sqParse = new SimpleQueryParser(analyzer, "content"); break;
                default:
                    System.out.println("ERR: Unknown query parser type!");
                    reader.close();
                    directory.close();
                    System.exit(1);
            }

            /* Continually allow a user to pass queries to the parser until the
             * special keyword '!stop' is passed to terminate execution */
            queryProcess();

            // Final cleanup
            if (PROG_TRACE) { printTrace("Closing the DirectoryReader, Directory..."); }
            reader.close();
            directory.close();
        }
        catch(IOException e) {
            // An I/O exception happened, presumably during file handle
            System.err.println(e.getMessage());
            System.exit(1);
        }
        catch(Exception e) {
            // An unknown, unexpected error occured
            System.err.println(e.getMessage());
            System.exit(1);
        }
    }

    /** Runs a check on the arguments provided to the program. It checks for
      * the user to specify the location of the corpus and the location of
      * where to store the index when created.
      * @param args The arguments passed to the program */
    public static void argumentCheck(String[] args) {
        try {
            corpus = dirCheck(args[0]);

            /* Iterate through all the arguments passed to the system, flagging
             * an error if one is unrecognized */
            for(int i=1; i<args.length; i++) {
                switch(args[i]) {
                    // Overwrite the index instead of appending
                    case "-regen":
                        om = IndexWriterConfig.OpenMode.CREATE;
                        break;
                    
                    // Toggle program tracing
                    case "-trace":
                        PROG_TRACE = true;
                        break;
                    
                    // Change the type of query parser to use
                    case "-parse":
                        parserType = Byte.parseByte(args[i+1]);
                        i++;
                        break;

                    // Modify the location of the index
                    case "-index":
                        index = dirCheck(args[i+1]);
                        i++;
                        break;
                    
                    // Toggle generation of Heaps' Law coordinate data
                    case "-heap":
                        heap = dirCheck(args[i+1]);
                        heaper = new Heaper();
                        i++;
                        break;

                    // Unrecognized parameter was passed
                    default:
                        throw new Exception("Insufficient parameters!");
                }
            }
        }
        catch(Exception e) {
            // Print usage information for the program
            System.err.println(e.getMessage());
            System.err.print(
                "usage: java Lucene <corpus> [options]\n"+
                "Options:\n"+
                "  -index dir   Change where to store the index\n"+
                "  -regen       Overwrite the index\n"+
                "  -trace       Trace program execution\n"+
                "  -heap dir    Specify a directory to generate heap data\n"+
                "  -parse n     Change the query parser used\n"+
                "     0: QueryParser          1: SimpleQueryParser   \n"
            );
            System.exit(1);
        }
    }

    /** Processes the corpus specified, generating Documents with Fields for
      * the appropriate information. (See the header for the indexed fields.)
      * @return A list of the generated Document instances */
    public static ArrayList<Document> corpusProcess() {
        ArrayList<Document> L = new ArrayList<>();

        /* Get the list of files in the corpus directory, removing any entries
         * afterward that have filenames that start with a period */
        corpus_list = recurseDirectory(corpus);

        for(int i=corpus_list.size()-1; i>= 0; i--) {
            String fname = corpus_list.get(i);
            fname = fname.substring(fname.lastIndexOf('/')+1);

            if (fname.charAt(0) == '.')
                corpus_list.remove(i);
        }

        /* Iterate through all the files found to be in the corpus, processing
         * their text and parsing them via the Cranfield specification */
        try {
            java.util.Collections.sort(corpus_list);

            for(int f = 0; f < corpus_list.size(); f++) {
                // tmp is a string for building document content
                // doc is the Document to be added to the IndexWriter
                // fData is the full document's set of lines
                String tmp = "";
                Document doc = new Document();
                ArrayList<String> fData = readFile(corpus_list.get(f));

                /* Iterate through the text of the document until the milestone
                 * headers are located. Each header indexes the prior's content,
                 * with the exception of ".T", which does nothing. At the end,
                 * the document content field is added, as well as a unique ID
                 * field for future identification */
                for(int i=0; i<fData.size(); i++)
                    switch(fData.get(i)) {
                        case ".T": break; // Do nothing
                        case ".A":
                            doc.add(new TextField("title", tmp.trim(),
                                Field.Store.YES));
                            tmp = "";
                            break;
                        case ".B":
                            doc.add(new TextField("author", tmp.trim(),
                                Field.Store.YES));
                            tmp = "";
                            break;
                        case ".W":
                            doc.add(new StringField("bib", tmp.trim(),
                                Field.Store.YES));
                            tmp = "";
                            break;
                        default:
                            tmp += " " + fData.get(i);
                    }
                doc.add(new StoredField("id", f));

                /* Term vectors are important for getting term stats from the
                 * index, so a custom field has to be generated for the body
                 * of a document */
                FieldType fType = new FieldType();
                fType.setStored(true);
                fType.setTokenized(true);
                fType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS);
                fType.setStoreTermVectors(true);
                fType.setStoreTermVectorPositions(true);
                doc.add(new Field("content", tmp, fType));

                if (PROG_TRACE) { printTrace("Doc added: "+doc.get("title")); }
                L.add(doc);

                /* If the user wants to save Heaps' Law data to the disk, then for this document we must
                 * generate a TokenStream using the analyzer, iterate through its tokens, and generate
                 * data points. We then close the TokenStream to prevent exceptions */
                if (heaper != null) {
                    // ts is the TokenStream for the document body
                    // cta is used for accessing the text of the tokens in the TokenStream
                    TokenStream ts = analyzer.tokenStream(null, doc.getField("content").stringValue());
                    CharTermAttribute cta = null;

                    /* Add a document to the heaper, reset the TokenStream, and then iterate
                     * through all of its tokens, adding them to the heaper and generating
                     * Heaps' Law data points */
                    if (PROG_TRACE) { System.out.println("  Heaps' Law data in progress..."); }
                    heaper.addDoc();
                    ts.reset();
                    while(ts.incrementToken()) {
                        cta = ts.getAttribute(CharTermAttribute.class);
                        heaper.docAddTerm(heaper.docs()-1, cta.toString());
                        heaper.addPoint(heaper.docs()-1);
                    }
                    ts.close();
                }
            }

            /* All of the documents have been processed, and thus we must save Heaps' Law information
             * to the disk if it was requested */
            if (heaper != null) {
                if (PROG_TRACE) { printTrace("Saving Heaps' Law data to Disk..."); }
                heaper.save(heap);
            }
        }
        catch(IOException e) {
            System.err.println(e.getMessage());
        }

        return L;
    }

    /** Allows continual processing of queries until the stop keyword has been
      * reached. A couple of special commands are available that allow for
      * insight into the indexed corpus (such as to fulfill the program's
      * purpose of getting tf, cf, df, and idf values). */
    public static void queryProcess() throws ParseException, IOException {
        // kbd is the scanner being used to read in user queries
        // rawQuery stores the raw query text the user entered
        Scanner kbd = new Scanner(System.in);
        String rawQuery = "";

        // que stores all the queries to be executed on the index
        Query[] que = {
            new MatchAllDocsQuery(),
            new TermQuery(new Term("content", "alligator")),
            new TermQuery(new Term("content", "beautiful")),
            new TermQuery(new Term("content", "chairman")),
            new TermQuery(new Term("content", "eulogies")),
            new TermQuery(new Term("content", "voyage")),
            new TermQuery(new Term("title", "the")),
            new TermQuery(new Term("author", "william")),
            null, // (NOT alligator) AND (NOT chairman)
            null, // alligator OR chairman
            new PrefixQuery(new Term("content", "ancest")),
            new PrefixQuery(new Term("content", "voyage")),
            new WildcardQuery(new Term("content", "b?ats")),
            new WildcardQuery(new Term("author", "s*n")),
            new FuzzyQuery(new Term("content", "twilit")),
            new FuzzyQuery(new Term("title", "gods")),
            new RegexpQuery(new Term("title", "[0-9]{4}")),
            new RegexpQuery(new Term("content", "account[a-z]+")),
            new RegexpQuery(new Term("author", "[a-z]")),
            null,
            null,
            null,
            null,
            new TermRangeQuery("title", new BytesRef("1800"), new BytesRef("1899"), true, true),
            new TermRangeQuery("author", new BytesRef("b"), new BytesRef("c"), true, true),
            null
        };

        BooleanQuery.Builder builder = new BooleanQuery.Builder();
        builder.add(new MatchAllDocsQuery(), BooleanClause.Occur.MUST)
               .add(new BooleanClause(que[1], BooleanClause.Occur.MUST_NOT))
               .add(new BooleanClause(que[3], BooleanClause.Occur.MUST_NOT));
        que[8] = builder.build();

        builder = new BooleanQuery.Builder();
        builder.add(new BooleanClause(que[1], BooleanClause.Occur.SHOULD))
               .add(new BooleanClause(que[3], BooleanClause.Occur.SHOULD));
        que[9] = builder.build();

        PhraseQuery.Builder pq_builder = new PhraseQuery.Builder();
        pq_builder.add(new Term("content", "not"), 0)
                  .add(new Term("content", "kind"), 2);
        que[19] = pq_builder.build();

        pq_builder = new PhraseQuery.Builder();
        pq_builder.add(new Term("content", "narrative"), 0)
                  .add(new Term("content", "the"), 2);
        que[20] = pq_builder.build();

        MultiPhraseQuery.Builder mpq_builder = new MultiPhraseQuery.Builder();
        mpq_builder.add(new Term("content", "not"))
                   .add(new Term[] { new Term("content", "kind"), new Term("content", "cheery"), new Term("content", "generous") }, 1);
        que[21] = mpq_builder.build();

        mpq_builder = new MultiPhraseQuery.Builder();
        mpq_builder.add(new Term[] { new Term("title", "of"), new Term("title", "to") })
                   .add(new Term("title", "the"));
        que[22] = mpq_builder.build();

        ArrayList<Query> dmq_bits = new ArrayList<>();
        BooleanQuery.Builder bq = new BooleanQuery.Builder(), bq_bit = new BooleanQuery.Builder();
        bq_bit.add(new TermQuery(new Term("title", "stories")), BooleanClause.Occur.SHOULD)
              .add(new TermQuery(new Term("title", "narrative")), BooleanClause.Occur.SHOULD);
        bq.add(bq_bit.build(), BooleanClause.Occur.MUST)
          .add(new TermQuery(new Term("title", "life")), BooleanClause.Occur.SHOULD)
          .add(new TermQuery(new Term("title", "little")), BooleanClause.Occur.SHOULD);
        dmq_bits.add(bq.build());
        dmq_bits.add(new TermQuery(new Term("content", "fruitful")));
        que[25] = new DisjunctionMaxQuery(dmq_bits, (float) 1.25);

        int index = 0;

        /* Given that querying only terminates when the special command is
         * reached, there is no suitable condition for this loop; therefore,
         * it runs infinitely unless the function is forced to return */
        while(true) {
            if (index < que.length) {
                query = que[index]; index++;
                System.out.println("Executing "+query.toString());
            }
            else {
                break;
                // System.out.print("\nQuery > ");
                // rawQuery = kbd.nextLine();
                // if (rawQuery.charAt(0) == '!' && rawQuery.charAt(1) != '!') {
                //     // If the '!stop' command is found, break from the loop
                //     // If other commands are found, skip the rest of the loop body
                //     if (queryProcessSpecial(rawQuery)) { break; }
                //     else { continue; }
                // }
                // else if (rawQuery.charAt(1) == '!')
                //     rawQuery = rawQuery.substring(1);

                // // The query is parsed by the appropriate parser
                // switch(parserType) {
                //     default:
                //     case 0: query = qParse.parse(rawQuery); break;
                //     case 1: query = sqParse.parse(rawQuery); break;
                // }
            }

            /* Print the top results of the query. The documetn ID, score
             * against the query, and document title are all printed */
            System.out.printf("%7s : %10s : %s\n", "ID", "Score", "Title");
            result = iSearch.search(query, TOP_RESULT_COUNT).scoreDocs;
            for(ScoreDoc doc : result)
                System.out.printf("Doc %3d : %10f : %s\n", doc.doc,
                    doc.score, iSearch.doc(doc.doc).get("title"));
        }

        kbd.close();
    }

    /** Allows processing of special query commands while querying is being executed.
      * (That is, a command is passed with '!' as a prefix, and '!' is not escaped
      * by a leading '!'.) A few commands are made available.
      * @return True if querying should terminate, or false in other cases */
    public static boolean queryProcessSpecial(String rawQuery) {
        switch(rawQuery.split(" ")[0]) {
            // This command stops execution of querying
            case "!stop": return true;

            // This command prints term information
            case "!term": cmdTerm(rawQuery.split(" ")); break;

            // This command prints explanation information
            case "!explain":
                String rq = "";
                try {
                    rq = rawQuery.substring(rawQuery.indexOf(" ")+1);
                    rq = rq.trim().substring(rq.indexOf(" ")+1);
                    cmdExplain(rawQuery.split(" ")[1], rq);
                }
                catch(Exception e) {
                    cmdExplainUsage();
                }
                break;

            // Unrecognized command
            default:
                System.out.println("The system doesn't recognize the command!");
        }
        return false;
    }

    /*************************** COMMAND FUNCTIONS ****************************/
    /* These functions are listed in the order that they were created to
     * execute the main code of special commands for the querying interface. */

    /** Executes the !term command for the system, printing information about a
      * term, range of terms, or all terms. It may also print terms to a file
      * if requested. The syntax of the term is as follows:
      *
      * !term <TERM|!all|!n> [fname]
      * @param cmd The command text (the raw query) split at spaces */
    public static void cmdTerm(String[] cmd) {
        // Display usage text if the command isn't used correctly
        if (cmd.length < 2 || cmd.length > 3) {
            cmdTermUsage();
            return;
        }

        // topn is the number of terms that most-frequency occur to print
        // fname is the name of the file to write the information to
        // term is the term to be printed, if any
        // head is the header to be printed
        // w is a writer that will be used to write information to a file
        int topn;
        String fname = (cmd.length == 3 ? cmd[2] : null), term = cmd[1], head;
        BufferedWriter w = null;

        try {
            if (fname != null) { w = new BufferedWriter(new FileWriter(fname));}
            head = String.format("%20s %5s %6s %10s %5s\n", "Term", "DF", "CF",
                "IDF", "TF");

            /* Generate the LToken list ONLY if it hasn't been generated before.
             * The list is generated here such that numerous "!term" commands
             * can be executed without recomputing all the LTokens necessary */
            if (LTL == null) {
                // LTH is a table of LTokens, indexed by terms to prevent
                // duplication of token generation
                // tEnum is the TermsEnum for the current document
                // pEnum is the PostingsEnum for the cur term in the cur doc
                // tok is a temporary storage variable for LToken generation
                Hashtable<String,LToken> LTH = new Hashtable<>();
                TermsEnum tEnum = null;
                PostingsEnum pEnum = null;
                LToken tok;
                
                /* Iterate through every document, fetching its TermsEnum to
                 * append all the terms of the corpus to the hashtable of
                 * LTokens. A new LToken is only generated if the table
                 * doesn't contain that term presently; elsewise, the term's
                 * tf for the document is updated using the pEnum instance */
                for(int i=0; i<reader.numDocs(); i++) {
                    tEnum = reader.getTermVector(i, "content").iterator();

                    while(tEnum.next() != null) {
                        String tmp = tEnum.term().utf8ToString();
                        pEnum = tEnum.postings(null);
                        pEnum.nextDoc();

                        if (!LTH.containsKey(tmp)) {
                            tok = new LToken(reader.numDocs(), tmp);
                            tok.term = tmp;
                            tok.df = reader.docFreq(tok.termObj);
                            tok.cf = reader.totalTermFreq(tok.termObj);
                            tok.idf = Math.log10(1.0*reader.numDocs()/tok.df);
                            tok.tf[i] = pEnum.freq();

                            LTH.put(tmp, tok);
                        }
                        else
                            LTH.get(tmp).tf[i] = pEnum.freq();
                    }
                }
                LTL = Collections.list(LTH.elements());
                Collections.sort(LTL, Collections.reverseOrder());
            }

            /* If the first character of the 'term' is an exclamation point, then
             * the user is printing a range of terms, or all term information. If
             * there isn't an exclamation point, then a specific term was chosen */
            if (term.charAt(0) == '!') {
                /* Print the heading line and then, if specified, print all
                 * the token information for every token (or range) to-screen */
                System.out.print(head);
                if (fname != null) { w.write(head); }

                if (!term.equals("!all")) {
                    topn = Integer.parseInt(term.substring(1));
                    for(int i=0; i<topn && i<LTL.size(); i++)
                        writeToken(LTL.get(i), w);
                }
                else
                    for(int i=0; i<LTL.size(); i++)
                        writeToken(LTL.get(i), w);
            }
            else {
                /* Iterate through all of the tokens in the LTL list. If the
                 * token being searched for is found, print it's information.
                 * If it isn't found, display an error message */
                for(LToken lt : LTL)
                    if (lt.term.equals(term)) {
                        System.out.print(head);
                        writeToken(lt, w);
                        return;
                    }
                System.out.println("The index doesn't contain '"+term+"'");                
            }

            if (fname != null) { w.close(); }
        }
        catch(Exception e) { cmdTermUsage(); System.out.println(e.getMessage()); }
    }

    /** Executes the !explain command for the system, printing information about
      * how a document scored against a query.
      *
      * !explain <doc> <query>
      * @param docID The document ID to explain, as a string
      * @param rq The query to explain the document against */
    public static void cmdExplain(String docID, String rq) {
        try {
            if (rq.length() == 0) { throw new Exception(""); }

            // doc is the document 
            // q is the final query instance generated by the parser
            int doc = Integer.parseInt(docID);
            Query q = null;

            switch(parserType) {
                case 0: q = qParse.parse(rq); break;
                case 1: q = sqParse.parse(rq); break;
            }

            System.out.println(iSearch.explain(q, doc).toString());
        }
        catch(Exception e) {
            System.out.println(e.getMessage());
            cmdExplainUsage();
        }
    }

    /** Prints the usage for the !term command. */
    public static void cmdTermUsage() {
        System.out.println("usage: !term <TERM|!all|!n> [fname]");
    }

    /** Prints the usage for the !explain command. */
    public static void cmdExplainUsage() {
        System.out.println("usage: !explain <doc> <query>");
    }

    /**************************** HELPER FUNCTIONS ****************************/
    /* These functions are listed in the order that they were created in to
     * provide assistance to the main procedure functions above. They typically
     * do a very simple procedure, such as generating a list of filenames or
     * printing a simple trace statement. */

    /** Prints a single trace statement to the screen.
      * @param t The string to print after the trace prefix */
    public static void printTrace(String t) {
        System.out.println("PROG: "+t);
    }

    /** Performs a quick check on an expected directory, appending a final
      * slash if one isn't detected.
      * @param dir The directory name to check the last slash of
      * @return The corrected name of the directory if no slash was detected,
      *   or the given directory name if one was detected */
    public static String dirCheck(String dir) {
        if (dir.contains("\\")) { dir = dir.replaceAll("\\", "/"); }
        return dir + (dir.charAt(dir.length()-1) != '/' ? "/" : "");
    }

    /**
     * Recursively digs through a folder to create a list of all files in the
     * given parent directory.
     * @param directory The directory being recursed to generate filenames
     * @return A list of strings representing all the filenames
     */
    public static ArrayList<String> recurseDirectory(String directory) {
        ArrayList<String> L = new ArrayList<>();
        File dir = new File(directory);

        if (dir.isDirectory()) {
            // For every path in the directory, if the path is a directory, recurse
            // down to locate more files; otherwise, add the pathname to the list
            // of files, L
            for(File f : dir.listFiles())
                if (f.isDirectory())
                    L.addAll(recurseDirectory(directory+f.getName()+"/"));
                else
                    L.add(directory+f.getName());

        }
        else {
            // ERROR: A directory wasn't specified
            System.err.printf("ERR: '%s' is not a directory!\n", directory);
            System.exit(1);
        }
        
        return L;
    }

    /** Reads in all the lines of a raw text file, putting those lines into a
      * list that gets returned.
      * @param fname The name of the file to open and read
      * @return The list of lines of the file (excluding blank lines) */
    public static ArrayList<String> readFile(String fname) throws IOException {
        // line is temporary storage for a line read from teh file
        // file is a list of all the lines in the file
        String line;
        ArrayList<String> file = new ArrayList<>();

        // Iterate through all the lines of the file, adding them if they aren't
        // blank lines. Return the final list of lines afterward
        BufferedReader r = new BufferedReader(new FileReader(fname));
        while((line = r.readLine()) != null)
            if (line.length() > 0)
                file.add(line);
        r.close();

        return file;
    }

    /** Writes a single token both to the screen and to the writer specified.
      * If no writer is specified, then the token is only printed to-screen.
      * @param token The LToken to print the information of
      * @param w The writer to write the token's information to (or null) */
    public static void writeToken(LToken token, BufferedWriter w) throws IOException {
        if (w != null) { w.write(token.info()+"\n"); }
        System.out.println(token.info());
    }
}