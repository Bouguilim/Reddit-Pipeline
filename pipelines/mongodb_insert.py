from pymongo import MongoClient
from utils.constants import MONGO_URL

def insert_data_to_mongodb(game_name, **kwargs):

    ti = kwargs['ti']
    cleaned_data = ti.xcom_pull(task_ids='reddit-transform')

    # Connect to MongoDB
    client = MongoClient(MONGO_URL)
    db = client['reddit_data']

    # Create a collection with the game name
    collection_name = '_'.join(game_name.split())
    collection = db[collection_name]

    # Insert data into MongoDB
    collection.insert_many(cleaned_data)

    print(f"Data inserted into MongoDB collection '{collection_name}'.")