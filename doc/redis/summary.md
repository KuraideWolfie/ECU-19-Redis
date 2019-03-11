# Summary
## Introduction
### About Redis
Redis is a non-relational database management system with basic data structure support for lists, hashes, sets, and ordered sets (referred to as zsets). Documents are not tied together as relations, but are stored in the form of key-value pairs. It can be configured to run as a cluster, where there are multiple 'nodes' that handle executed commands to the system. _(The minimal cluster is 3 masters with 3 workers, each worker backing up a unique master.)_

Redis offers two advantageous features - sharding and replication:
  + Redis worker nodes replicate master nodes, and automatically synchronize with the cluster on startup. The worker pings for updates on an interval using an internal port, and will failover a master if it does not receive an update within a certain time increment.ext install yzane.markdown-pdf
  <br /><br />
  _Upon return from being down, the master will, typically, be changed to a worker for the new master and replicate its data. Should the new master go down, then the original will retake its place._
  + Sharding is usually done automatically by Redis; however, for the purposes of the project, this was overriden using a unique concept of hash tagging and key slots. _What this means is that key-value pairs can be forced to particular master nodes via including a value that will hash to a particular slot using `{}`. For example, `{yum}example` will hash to the same slot as `yum`, whereas `example` alone will be hashed to the slot for `example`._
  <br /><br />
  _Every master node in a cluster has a particular number of 'slots' that it has control over. There are, in sum, 16,384 slots, so each master in a 3-master, 3-worker cluster covers ~5,400 slots each._

### Goals
There were a couple of questions investigated:
  + Could a Boolean Retrieval index be efficiently queried using Redis set operations
  + Could a Redis cluster be used to offer availability via replication
  + Could documents be partitioned using Redis' sharding capacities

The Boolean Retrieval index being constructed would regard the Project Gutenberg corpora from the WWW, comprised of over 50k documents originally at 20 GB of disk space.

## Procedure
### Corpus Cleaning
The first major step was cleaning the Gutenberg corpora, and reducing the number of files and space that they take (as well as minimalizing redundant processing using Redis). The following steps were performed:
  + Gutenberg Project licensure was migrated from the end of each document to a new document in a separate folder, as to preserve the license as per its terms.
  + Documents were segmented, by ID, in groups of 1,000 into directories - for example, `0-1` storing files with IDs of 000 to 999.
  + Languages were extracted from the documents, and they were segmented by language. All languages other than English were extracted from the corpora.
  + Some select documents, whose content was unusable for the project, were partitioned away from the corpora - for example, documents containing human genome and mathematical constant information.
  + Documents that had multiple variants were segmented out, and the alternate versions removed. (The alternate versions were solely different encodings of the files in question.)

After performing processing, instead of taking 50,000+ files and ~20 GB of disk space, the corpus was comprised of ~42,000 files (excluding licenses) and ~16 GB of space.

### Cluster Setup
To setup the Redis cluster, the individual nodes had to be configured, then joined using the following procedure:
  + Redis installation _(requiring root privilege on Linux)_
    + Downloading and extraction of Redis as a TAR.GZ file
    + Running of the script `install_server.sh` in installation files to make Redis run on startup
  + Cluster setup
    + Correction of the configuration file for Redis _(made during the run of `install_server.sh`)_, including a password, master authentication password, and cluster information:
      ```
      requirepass [pass]
      masterauth [pass]
      port 6379
      cluster-enabled yes
      cluster-config-file /nodes.conf
      cluster-node-timeout 5000
      appendonly yes
      ```
    + Creation of the cluster using redis-cli
      + `redis-cli --cluster create [node]:[port] ... [node]:[port] --cluster-replicas 1 -a [pass]` created the cluster. `[pass]` was required because of the presence of the requirepass field in the configuration file
      + `redis-cli --cluster check [node] [port] -a [pass]` checked the status of the cluster

After executing these steps, a basic 3-master, 3-worker cluster was running, with each worker replicating a unique master. The port for connection was the default - 6379 - with the port the nodes use to communicate amongst each other being 16379. The cluster also required a password for executing commands.

### Program Development
The following was done in setup:
  + The Python library `redis-py-cluster` was installed to interface with Redis
  + A Query class was made for parsing B.R. queries with the following syntax:
    + `<space>` represented and, `|` represented or, and `!` represented not; queries could be grouped using `[]`
    + The precedence for parsing was and, or, then not; for example, `blue !stripe|dot` parses to `blue AND (NOT stripe OR dot)`, not `(blue AND NOT stripe) OR dot`; the query `[blue !stripe]|dot` would result in the latter. See **Figure 1**
  + Specific key slots were determined for the master nodes - 1 each per master - that could be used to force documents to their pre-determined nodes as assigned by the program. Methods of doing this were:
    + Using the command `cluster keyslot <key>` in redis-cli
    + Using the redis-py-cluster library

The program, after establishing a successful connection to Redis, allowed the user to enter where the corpora documents are. It constructed a B.R. index for the documents of the specified location, and sent the raw text data to the server as well. After performing this processing, querying was allowed using the aforementioned syntax.
  + Documents were partitioned in a round-robin format - that is, the first document found in the folder was sent to Master 1, the second to 2, the third to 3, then the fourth to 1, etc.
  + After the entire docset was partitioned, boolean retrieval indices for only that subset were generated and sent to the respective master using _hash tagging_ and _key slots_ for each node. See **Figure 2**

During corpus processing, a pattern was discerned in each of the documents of the corpora, including a Title, Author, and Release Date tags. These metadata tags were used to provide specific titles for results when executing queries. Testing was also performed on the querying interface to ensure that proper results were returned, such as `!dark|[orange ball]` and `!arch !dread [happy|joy pleasure]` to test grouping and the three fundamental operations - and, or, and not.

### Master Failover Test
After ensuring the program worked, testing the replication of the application was priority. This was done by using a special command in the program, `~sys`, to discern which nodes were master nodes in the cluster, with the first being selected for failover. The following procedure was done, with terms such as `happy` and `joy` used to discern if the documents for the failed master were still accessible.
  + The master node to be failed over was accessed using SSH via terminal. At the same time, the application was up and running to the point of query execution.
  + The command `~sys` was run to ensure the master node was recognized as alive, with `~docset` being used to ascertain which documents were on that node. A simple query, such as `happy`, was then run and results documented.
  + The master was failed over using the below commands:
    ```
    redis-cli -a [pass]  (Via terminal)
    shutdown save        (In redis-cli)
    ```
    Afterward, the same queries were executed to test if the results were the same. The master was revived using SSH with the command `redis-server ./cluster/redis.conf --daemonize yes`, where `.cluster/redis.conf` is the configuration file from prior cluster setup.

Testing was done using queries that were guarenteed to have more than 10 documents in their results, as this would assert that at least 1 document ID would be on the failed over master node, given that a subset of 15 documents was used for testing - 5 per master node. See **Supplements > Master Failover test: Program Output** below.

## Conclusion
+ A Boolean Retrieval index could successfully be constructed and queried using set operations in Redis. Not explained earlier is the concept of using Redis' set intersection operation for and, union for or, and difference for not, nor is the procedure for storing intermediary query results as temporary key-value pairs. See **Figure 3** for an example query execution.
+ Documents were able to be partitioned using Redis' hash tagging feature and known, specific key slots allocated to each of the master nodes. The workers synchronized successfully with their corresponding master nodes, replicating the data and offering data reliability on the failover of a master.

## Supplements
### Figures
<div style="text-align: center;">
 <img alt="Sample Query Parse Tree" src="./img/figure-1a.png" style="height: 150px; border: 1px purple solid;"> <img alt="Sample Query Parse Tree Alt" src="./img/figure-1b.png" style="height: 150px; border: 1px purple solid;">
 <p><i><b>Figures 1-a and 1-b</b>: Sample query parse trees, showing precedence and grouping</i></p>
</div>

<div style="text-align: center">
  <img alt="Document Partitioning Scheme" src="./img/figure-2.png" style="border: 1px purple solid;">
  <p><i><b>Figure 2</b>: Round-robin and Boolean Retrieval indexing procedure. Take notice the round-robin scheme evenly distributes documents amongst the master nodes</i></p>
</div>

<div style="text-align: center">
  <img alt="Sample Query Execution" src="./img/figure-3.png" style="border: 1px purple solid;">
  <p><i><b>Figure 3</b>: A sample query execution based on the query's parse tree. To solve the query, its parts are recursively solved, and those results stored intermediantly in Redis as temporary key-value pairs. The green block is the final result.</i></p>
</div>

### Master Failover Test: Program Output
The following is program output from Redis when the master failover test was performed, with a simplistic query performed to showcase the replication features made the database realiable. Take notice:
  + The first master on the first useage of `~sys` is **150.216.79.32**; however, after the master was turned off, the first master is listed as **150.216.79.35**. The number of workers also changes from 1 to 0.
  + After the master is brought back - the third usage of `~sys` - the number of workers changes from 0 back to 1; however, the first master listed is still **150.216.79.35**. The node with an ending octet of **32** is now the worker of **35**.
  + There is output, on the second attempt to query the cluster, of something having gone wrong; this is due to the connection recognizing one of the master's is down, and requires a refresh of what nodes are in the cluster.

```
[mnmorgan@dhcp-10-35-54-160 redis]$ python3 main.py
Connecting to server...
Connection successful
Clear the database? (y/n) > n
Load corpus data? (y/n) > n

Type '~stop' to exit querying
Query > ~sys
Database Master Nodes
  150.216.79.32:6379 -> 7041 keys
    Memory: (Cur\Ttl -> 3.87M \ 7.64G), (RSS\LUA -> 14.74M \ 37.00K)
    Workers: 1
  150.216.79.34:6379 -> 8235 keys
    Memory: (Cur\Ttl -> 4.55M \ 7.64G), (RSS\LUA -> 18.12M \ 37.00K)
    Workers: 1
  150.216.79.33:6379 -> 9640 keys
    Memory: (Cur\Ttl -> 4.99M \ 7.64G), (RSS\LUA -> 161.61M \ 37.00K)
    Workers: 1

Query > ~docset
Document set for master nodes:
  Master 0:
    11 55 58 62 67 
  Master 1:
    5 56 60 64 8 
  Master 2:
    54 57 61 66 9 

Query > arm
There were 14 hits
     11 : Alice's Adventures in Wonderland
      5 : The United States' Constitution
     54 : The Marvellous Land of Oz
     55 : The Wonderful Wizard of Oz
     57 : Aladdin and the Magic Lamp
     58 : Paradise Regained
     60 : The Scarlet Pimpernel
     61 : The Communist Manifesto
     62 : A Princess of Mars
     64 : The Gods of Mars
     66 : The Dawn of Amateur Radio in the U.K. and Greece
     67 : The Black Experience in America
      8 : Lincoln's Second Inaugural Address, March 4, 1865
      9 : Lincoln's First Inaugural Address, March 4, 1861

Query > ~sys
Woops... Something went wrong; hold on a moment...
Woops... Something went wrong; hold on a moment...
Woops... Something went wrong; hold on a moment...
Woops... Something went wrong; hold on a moment...
Database Master Nodes
  150.216.79.35:6379 -> 7041 keys
    Memory: (Cur\Ttl -> 3.84M \ 7.64G), (RSS\LUA -> 14.48M \ 37.00K)
    Workers: 0
  150.216.79.34:6379 -> 8235 keys
    Memory: (Cur\Ttl -> 4.53M \ 7.64G), (RSS\LUA -> 18.12M \ 37.00K)
    Workers: 1
  150.216.79.33:6379 -> 9640 keys
    Memory: (Cur\Ttl -> 4.98M \ 7.64G), (RSS\LUA -> 161.61M \ 37.00K)
    Workers: 1

Query > arm
There were 14 hits
     11 : Alice's Adventures in Wonderland
      5 : The United States' Constitution
     54 : The Marvellous Land of Oz
     55 : The Wonderful Wizard of Oz
     57 : Aladdin and the Magic Lamp
     58 : Paradise Regained
     60 : The Scarlet Pimpernel
     61 : The Communist Manifesto
     62 : A Princess of Mars
     64 : The Gods of Mars
     66 : The Dawn of Amateur Radio in the U.K. and Greece
     67 : The Black Experience in America
      8 : Lincoln's Second Inaugural Address, March 4, 1865
      9 : Lincoln's First Inaugural Address, March 4, 1861

Query > ~sys
Database Master Nodes
  150.216.79.35:6379 -> 7041 keys
    Memory: (Cur\Ttl -> 3.87M \ 7.64G), (RSS\LUA -> 14.48M \ 37.00K)
    Workers: 1
  150.216.79.34:6379 -> 8235 keys
    Memory: (Cur\Ttl -> 4.55M \ 7.64G), (RSS\LUA -> 18.12M \ 37.00K)
    Workers: 1
  150.216.79.33:6379 -> 9640 keys
    Memory: (Cur\Ttl -> 4.99M \ 7.64G), (RSS\LUA -> 161.61M \ 37.00K)
    Workers: 1

Query > ~stop
```