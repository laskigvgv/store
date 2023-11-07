#!/bin/bash

# Wait for MongoDB to be ready
until mongosh --eval "db.stats()" &>/dev/null; do
    echo "Waiting for MongoDB to start..."
    sleep 1
done

# # Connect to the MongoDB container
# mongosh --host localhost --port 27017 -u $MONGO_USER -p $MONGO_PASSWORD --authenticationDatabase admin

# # Switch to your target database
# use Store

# # Insert data into a collection
# db.products.insert( { "product1": "100"} )

# # Run the Python script to add data
# python init_db.py


mongoimport --db store --collection products --file dummy_data/test.json
