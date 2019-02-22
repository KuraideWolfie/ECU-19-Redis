# What is Redis?
Redis is a non-relational database management system with basic data structure support for _lists_, _hashes_, _sets_, and _zsets_ (ordered sets). Documents are not tied together by relations (foreign and primary keys), and as such, SQL queries are not executed on this database. _(This is also referred to as a NOSQL database system.)_ Redis stores information in the form of documents, where a document is in the form of one of the aforementioned data structure types, or numerical/string representations.

Redis typically operates on a single-node basis, but can be configured to operate in a cluster mode, where there are a series of master nodes and worker nodes attached. Data is partitioned amongst the master nodes, and the worker nodes replicate the data of the masters such that, should a master node go down, one of the workers can take over and become a 'master' until the original is up and running again. (It's heavily recommended that for every master node in a cluster configuration, there is at least one worker node beside it to replicate its data.)

# Partitioning and Sharding
### **Partitioning**
Redis partitions data using hash slots - that is, each document being sent to the database is resolved to be one of these slots (ranged 0 to 16384). Each master node in a cluster is given a certain number of slots. _(For example, in a 6-node cluster, with 3 masters and 3 workers, 2 of the masters accomodate 5461 of the slots, with the tertiary 5462 slots.)_ Whatever slot the data resolves to determines the master node the data is sent to. Connection can be established to any of the nodes, since each stores references to the other nodes; however, preferably the full list of nodes would be made available on initial connect.

#### Forcing Slots
Keys can be forced to evaluate to a specific slot by enclosing a portion of the key within `{}` - called a **hash tag**. For example, `{0}key` would evaluate to slot 13907, since `{0}` would be used for the evaluation. In a default 3-master, 3-worker cluster, this would send data to the third master - aka the one that holds the last 5,400 slots. The below is sample output from a default cluster showing this behavior. _(redis-cli was used to produce this output.)_

```
127.0.0.1:6379> cluster keyslot 0
(integer) 13907
127.0.0.1:6379> cluster keyslot {0}sample
(integer) 13907
127.0.0.1:6379> cluster keyslot {0}newsample
(integer) 13907
127.0.0.1:6379> cluster keyslot 2
(integer) 5649
127.0.0.1:6379> cluster keyslot 3
(integer) 1584
```

The slot that a key would evaluate to can be discerned using `cluster keyslot <key>` in redis-cli, or via a redis cluster API. Information is available at https://redis.io/commands/cluster-keyslot.

### **Sharding**
The worker nodes in a cluster occasionally ping the master nodes, checking if there is any data to be replicated. If there is, then the data is eventually duplicated by the nodes. _(This, in turn, doubles the amount of memory storage required for data.)_ If a worker node detects that a master is down, then after a predefined amount of time, the worker takes over the role of master, and dishes any data requested that it has access to.