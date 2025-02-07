# Storing XML Files in MongoDB Using Kafka

This project demonstrates how XML files are converted into JSON and then stored in MongoDB using Kafka. To achieve this, the following components interact with each other:

- **Kafka Broker, Zookeeper, Schema Registry**  
- **XML File Transformer**  
- **Kafka Connector for MongoDB**  
- **XML File Generator**  

---

## Requirements and Development Environment

### Development Environment Specifications  
- **Operating System:** Ubuntu 22.04  
- **Tools:** Docker, Docker Compose  

### Software Versions  
- **Kafka UI:** Latest  
- **Zookeeper:** cp-zookeeper:7.5.0  
- **Kafka:** cp-kafka:7.5.0  
- **Schema Registry:** cp-schema-registry:7.5.0  
- **FilePulse:** kafka-connect-file-pulse:2.13.0  
- **MongoDB:** mongo:4.4.1  
- **XML Generator:** xmlgen:0.1.0  

---

## Running the Code  

All the above-mentioned software components are started using Docker Compose with the following command:  
```bash
sudo docker compose up -d
```

After starting, we wait until all resources are ready and the Kafka UI interface is available at `{ip-address}:8080`.

---

## Setting Up Kafka Topics and File-Pulse Configuration  

The next step is to create a Kafka topic and add the File-Pulse configuration via the Kafka UI.

```json
{
    "connector.class": "io.streamthoughts.kafka.connect.filepulse.source.FilePulseSourceConnector",
    "fs.scan.directory.path": "/tmp/kafka-connect/examples/",
    "fs.scan.interval.ms": "10000",
    "fs.listing.class": "io.streamthoughts.kafka.connect.filepulse.fs.LocalFSDirectoryListing",
    "fs.scan.filters": "io.streamthoughts.kafka.connect.filepulse.scanner.local.filter.RegexFileListFilter",
    "file.filter.regex.pattern": ".*\\.xml$",
    "tasks.reader.class": "io.streamthoughts.kafka.connect.filepulse.fs.reader.LocalXMLFileInputReader",
    "offset.strategy": "name",
    "fs.listing.directory.path": "/tmp/kafka-connect-data/",
    "topic": "kndemo-topic-2",
    "internal.kafka.reporter.bootstrap.servers": "cp-kafka:29092",
    "tasks.file.status.storage.bootstrap.servers": "cp-kafka:29092",
    "internal.kafka.reporter.topic": "connect-file-pulse-status",
    "fs.cleanup.policy.class": "io.streamthoughts.kafka.connect.filepulse.fs.clean.DeleteCleanupPolicy",
    "tasks.max": 1
}
```

### Retaining Processed Files  

If processed files should not be deleted, the cleanup policy can be adjusted as follows:  
```json
"fs.cleanup.policy.class": "io.streamthoughts.kafka.connect.filepulse.fs.clean.LogCleanupPolicy"
```

---

## Connecting Kafka to MongoDB  

The connection is established using a Kafka Connector plugin located in the `kafka-connect/jars` directory. This directory contains all deployed plugins. A list of available plugins can be retrieved with the following command:  
```bash
curl localhost:8083/connector-plugins | json_pp
```

---

## Creating Databases and Collections in MongoDB  

### Option 1: Creating via MongoDB Compass  

If MongoDB Compass is installed, a database named `kafka` and a collection named `data` can be created using the following URI:  
```
mongodb://root:*****@<IP>:27017/?tls=false&authMechanism=DEFAULT
```

### Option 2: Manual Creation in MongoDB Container  

```bash
docker exec -it mongodb bash
mongo admin -u root -p root
use admin
db.changeUserPassword("root", "new-pass")
```

Authentication:  
```bash
use admin
db.auth("<username>", "<password>")
```

Creating the database and collection:  
```bash
use kafka
db.createCollection("data")
show databases
show collections
```

---

## Integrating MongoDB with Kafka via Kafka UI  

To store JSON data in MongoDB, the MongoDB Connector configuration file is set up through the Kafka UI:  

```json
{
    "connector.class": "com.mongodb.kafka.connect.MongoSinkConnector",
    "topics": "kndemo-topic-2",
    "connection.uri": "mongodb://root:root@mongodb:27017/?tls=false&authMechanism=SCRAM-SHA-256",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": false,
    "database": "kafka",
    "collection": "data"
}
```

Alternatively, this configuration can be applied without Kafka UI using a **curl** command:  
```bash
curl -X POST -H "Content-Type: application/json" --data-binary "@mongo-sink-config.json" http://localhost:8083/connectors
```

**Example `mongo-sink-config.json`:**  
```json
{
    "name": "mongo-sink",
    "config": {
        "connector.class": "io.confluent.connect.mongodb.MongoSinkConnector",
        "tasks.max": "1",
        "topics": "my_kafka_topic",
        "connection.uri": "mongodb://localhost:27017",
        "database": "my_database",
        "collection": "my_collection"
    }
}
```

---

## Starting the XML File Generator  

For testing, XML files can be generated and stored in a data folder. The XML generator is started alongside the Docker Compose file. XML files can be created via the REST API as follows:  

```bash
http://<IP>:8081/xmlfile/start
```

Once an XML file is uploaded to the specified folder, the FilePulse plugin detects the file, converts it into JSON, and stores it in MongoDB using the Kafka Connector. In the default configuration, processed files are automatically deleted.

The file generation process can be stopped using:  
```bash
http://<IP>:8081/xmlfile/stop
```

The interval for file creation and the number of files to generate can be configured using the `NUM_FILES` and `TIME_INTERVAL_IN_SEC` variables.

---

## References  

1. [Kafka-Connect FilePulse - Docker Compose](https://raw.githubusercontent.com/streamthoughts/kafka-connect-file-pulse/master/docker-compose.yml)  
2. [MongoDB Kafka Connector Konfiguration](https://github.com/mongodb/mongo-kafka/blob/master/config/MongoSinkConnector.properties)  
3. [Demo-Szene XML zu Kafka](https://github.com/confluentinc/demo-scene/blob/master/xml-to-kafka/docker-compose.yml)  
4. [Kafka Bildung - MongoDB University](https://github.com/mongodb-university/kafka-edu)  
5. [Demo-Szene - Confluent Inc](https://github.com/confluentinc/demo-scene/tree/master)  
6. [Streaming Data in Kafka - Blog](https://dev.to/fhussonnois/streaming-data-into-kafka-s01-e02-loading-xml-file-529i)  
7. [Kafka-Connect FilePulse - Docker Compose](https://raw.githubusercontent.com/streamthoughts/kafka-connect-file-pulse/v1.6.3/docker-compose.yml)  
