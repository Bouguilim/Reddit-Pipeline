#!/bin/bash
set -e

# Wait for MongoDB to start
until mongo --eval "print(\"waited for connection\")"; do
    sleep 5
done

# Create database and user
mongo <<EOF
use reddit_data
db.createUser({
    user: "admin",
    pwd: "admin",
    roles: [{ role: "readWrite", db: "reddit_data" }]
})
EOF

echo "MongoDB database and user created."