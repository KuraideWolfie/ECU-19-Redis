# Cluster Setup
The following commands will allow a basic cluster setup, and were used to setup the nodes/cluster for the project. The password used on the nodes is not included, nor is IP addresses about the nodes themselves.

Information about clusters is available at https://redis.io/topics/cluster-tutorial.

## Node Setup
The following instructions are useful for setting up a single node that will be used in a Redis cluster, and should be followed using a terminal. Information about the node will be stored in a folder called `cluster`.

1. Download and install the Redis DBMS system _(requires root privileges on Linux)_
  <br />`wget http://download.redis.io/redis-stable.tar.gz`
  <br />`tar xvzf redis-stable.tar.gz`
  <br />`cd redis-stable`
  <br /> `make`
  <br /> `sudo make install`
2. Install Redis server information for auto-run on startup
    + Create a directory called _cluster_ that will be where information about the node is stored
      <br />`mkdir ../cluster`
      <br />`cd ../cluster`
    + Run the _install\_server_ script (as notice, this script is being run from _/home/student/redis-stable/utils_ for this example)
      <br />`cd utils`
      <br />`./install_server.sh`
    + Provide the following parameters, where _6379_ is a port number, and the default
      <br />`6379`
      <br />`/home/student/cluster/redis.conf`
      <br />`/home/student/redis.log`
      <br />`/home/student/cluster/`
3. Remove the default configuration file, and recreate it with custom parameters
  <br />`rm ../../redis.conf`
  <br />`vi ../../redis.conf`
    ```
    CONFIGURATION FILE:
    -----------------------------------------
    requirepass [pass]
    masterauth [pass]
    port 6379
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
    appendonly yes
    ```

## Cluster Setup
1. Create the cluster using redis-cli
  <br />`redis-cli --cluster create [node]:[port] ... [node]:[port] --cluster-replicas 1 -a [pass]`

_(The following commands are prefixed with `redis-cli`.)_ You can get information about a node via the terminal on the node in question: `-p [port] cluster nodes | grep myself`. You can check on a node by using `--cluster check [node]` and reshard using `--cluster reshard [node] -a [pass]`.
