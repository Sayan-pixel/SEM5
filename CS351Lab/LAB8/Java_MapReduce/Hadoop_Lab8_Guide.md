# Hadoop Docker Installation & Custom Java MapReduce Guide

This document provides a complete, step-by-step walkthrough for setting up Hadoop on Docker and executing both built-in and custom Java MapReduce programs.

---

## Architecture Overview

- **Host OS**: Windows (with Docker Desktop)
- **Container Environment**: CentOS 7 running `apache/hadoop:3`
- **Cluster Services**:
  - `namenode` (HDFS NameNode - Web UI on port `9870`)
  - `datanode` (HDFS DataNode)
  - `resourcemanager` (YARN Resource Manager - Web UI on port `8088`)
  - `nodemanager` (YARN Node Manager)

---

## Phase 1: Cluster Configuration & Setup

### 1. Create `docker-compose.yaml`
In your working folder (`LAB8`), create `docker-compose.yaml`:

```yaml
version: "2"
services:
  namenode:
    image: apache/hadoop:3
    hostname: namenode
    command: ["hdfs", "namenode"]
    ports:
      - 9870:9870
    env_file:
      - ./config
    environment:
      ENSURE_NAMENODE_DIR: "/tmp/hadoop-root/dfs/name"
  datanode:
    image: apache/hadoop:3
    command: ["hdfs", "datanode"]
    env_file:
      - ./config
  resourcemanager:
    image: apache/hadoop:3
    hostname: resourcemanager
    command: ["yarn", "resourcemanager"]
    ports:
      - 8088:8088
    env_file:
      - ./config
    volumes:
      - ./test.sh:/opt/test.sh
  nodemanager:
    image: apache/hadoop:3
    command: ["yarn", "nodemanager"]
    env_file:
      - ./config
```

### 2. Create `config` File
Create a file named `config` (without extension) in the same directory:

```ini
CORE-SITE.XML_fs.default.name=hdfs://namenode
CORE-SITE.XML_fs.defaultFS=hdfs://namenode
HDFS-SITE.XML_dfs.namenode.rpc-address=namenode:8020
HDFS-SITE.XML_dfs.replication=1
MAPRED-SITE.XML_mapreduce.framework.name=yarn
MAPRED-SITE.XML_yarn.app.mapreduce.am.env=HADOOP_MAPRED_HOME=/opt/hadoop
MAPRED-SITE.XML_mapreduce.map.env=HADOOP_MAPRED_HOME=/opt/hadoop
MAPRED-SITE.XML_mapreduce.reduce.env=HADOOP_MAPRED_HOME=/opt/hadoop
YARN-SITE.XML_yarn.resourcemanager.hostname=resourcemanager
YARN-SITE.XML_yarn.nodemanager.pmem-check-enabled=false
YARN-SITE.XML_yarn.nodemanager.delete.debug-delay-sec=600
YARN-SITE.XML_yarn.nodemanager.vmem-check-enabled=false
YARN-SITE.XML_yarn.nodemanager.aux-services=mapreduce_shuffle
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.maximum-applications=10000
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.maximum-am-resource-percent=0.1
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.resource-calculator=org.apache.hadoop.yarn.util.resource.DefaultResourceCalculator
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.queues=default
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.default.capacity=100
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.default.user-limit-factor=1
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.default.maximum-capacity=100
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.default.state=RUNNING
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.default.acl_submit_applications=*
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.root.default.acl_administer_queue=*
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.node-locality-delay=40
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.queue-mappings=
CAPACITY-SCHEDULER.XML_yarn.scheduler.capacity.queue-mappings-override.enable=false
```

### 3. Start the Cluster
```powershell
docker pull apache/hadoop:3
docker compose up -d
```

Verify running containers:
```powershell
docker ps
```

Access Web Dashboard:
- NameNode UI: [http://localhost:9870](http://localhost:9870)
- ResourceManager UI: [http://localhost:8088](http://localhost:8088)

---

## Phase 2: Running Built-in Example MapReduce Job

1. Enter container shell:
   ```powershell
   docker exec -it lab8-namenode-1 bash
   ```
2. Create input files and HDFS directory:
   ```bash
   mkdir input
   echo "Hello Docker" > input/file2.txt
   echo "Hello Hadoop" > input/file1.txt
   hadoop fs -mkdir -p input
   hdfs dfs -put ./input/* input
   ```
3. Execute WordCount example:
   ```bash
   hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar wordcount input output
   ```
4. View result:
   ```bash
   hdfs dfs -cat output/part-r-00000
   ```

---

## Phase 3: Custom Java MapReduce Program

### 1. Create Source Files on Host Machine (`LAB8`)

#### `input.txt`
```text
Hello Docker
Hello Hadoop MapReduce
Welcome to Hadoop Custom MapReduce Java Program
```

#### `WordCountMapper.java`
```java
import java.io.IOException;
import java.util.StringTokenizer;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class WordCountMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();

    @Override
    public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        StringTokenizer itr = new StringTokenizer(value.toString());
        while (itr.hasMoreTokens()) {
            word.set(itr.nextToken());
            context.write(word, one);
        }
    }
}
```

#### `WordCountReducer.java`
```java
import java.io.IOException;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class WordCountReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private IntWritable result = new IntWritable();

    @Override
    public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }
        result.set(sum);
        context.write(key, result);
    }
}
```

#### `WordCountDriver.java`
```java
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCountDriver {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: WordCountDriver <input path> <output path>");
            System.exit(-1);
        }
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "word count");
        job.setJarByClass(WordCountDriver.class);
        job.setMapperClass(WordCountMapper.class);
        job.setCombinerClass(WordCountReducer.class);
        job.setReducerClass(WordCountReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
```

### 2. Copy Files to Container
In PowerShell on host machine:
```powershell
docker cp input.txt lab8-namenode-1:/tmp
docker cp WordCountDriver.java lab8-namenode-1:/tmp
docker cp WordCountMapper.java lab8-namenode-1:/tmp
docker cp WordCountReducer.java lab8-namenode-1:/tmp
```

### 3. Setup HDFS Directory & Upload Data
Inside container shell (`docker exec -it lab8-namenode-1 bash`):
```bash
cd /tmp
hdfs dfs -mkdir -p /user/root
hdfs dfs -mkdir -p /user/root/input
hdfs dfs -put input.txt /user/root/input/
```

### 4. Install Java Compiler (`javac`) in Container (If missing)
In CentOS container:
```bash
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
yum install -y java-1.8.0-openjdk-devel
```

### 5. Compile & Package Custom JAR
Inside `/tmp` in container shell:
```bash
javac -classpath $(hadoop classpath) -d . WordCountMapper.java WordCountReducer.java WordCountDriver.java
jar -cvf wordcount.jar *.class
```

### 6. Run Custom MapReduce Job & Verify Output
```bash
hadoop jar wordcount.jar WordCountDriver /user/root/input /user/root/output
hdfs dfs -cat /user/root/output/part-r-00000 > output.txt
cat output.txt
```

---

## Phase 4: Resolving IDE Red Underlines on Windows

To fix `import org.apache.hadoop...` red underlines in VS Code / Antigravity on Windows:

1. Copy JARs from Docker to local `./lib` directory:
   ```powershell
   mkdir lib
   docker cp lab8-namenode-1:/opt/hadoop/share/hadoop/common/hadoop-common-3.3.6.jar ./lib/
   docker cp lab8-namenode-1:/opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-core-3.3.6.jar ./lib/
   ```
2. In VS Code, go to **JAVA PROJECTS** (in sidebar) -> **Referenced Libraries** -> click `+` -> add the `.jar` files in `lib/`.
