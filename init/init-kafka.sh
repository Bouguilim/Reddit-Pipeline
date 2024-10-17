#!/bin/bash

# Wait for Kafka to be ready
while ! (echo > /dev/tcp/kafka/9092) >/dev/null 2>&1; do
  sleep 1
done

# Create reddit_post_topic
kafka-topics.sh --create --topic posts --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1

# Create reddit_comment_topic
kafka-topics.sh --create --topic comments --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
