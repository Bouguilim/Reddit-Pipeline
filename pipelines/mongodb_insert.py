from pymongo import MongoClient
import json
import os

def insert_data_to_mongodb(game_name, **kwargs):

    ti = kwargs['ti']
    json_file_path = ti.xcom_pull(task_ids='reddit-transform')

    # Connect to MongoDB
    client = MongoClient("mongodb://admin:admin@mongodb:27017/admin")
    db = client['reddit_data']
    print(f'#########{db}')

    # Create a collection with the game name
    collection_name = game_name
    collection = db[collection_name]

    # Load the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Insert data into MongoDB
    if isinstance(data, list):  # Ensure data is a list
        collection.insert_many(data)
    else:
        collection.insert_one(data)

    # Delete the JSON file after insertion
    os.remove(json_file_path)
    print(f"Data inserted into MongoDB collection '{collection_name}'.")

# Run the test
#insert_data_to_mongodb('bobo', './data/output/reddit_comments.json')
