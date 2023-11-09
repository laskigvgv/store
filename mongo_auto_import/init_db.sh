#!/bin/bash

# Wait for MongoDB to be ready
until mongosh --eval "db.stats()" &>/dev/null; do
    echo "Waiting for MongoDB to start..."
    sleep 1
done

mongoimport --db store --collection products --file dummy_data/test.json
