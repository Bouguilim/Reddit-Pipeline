from pyspark.sql import SparkSession
import requests
import json
import sys, os, time
import argparse
import psycopg2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import *

import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))  # Define the stopwords
    words = text.split()  # Split text into words
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)  # Join filtered words back into a string

def truncate_text(text, max_words=350):
    words = text.split()  # Split text into words
    if len(words) > max_words:
        words = words[:max_words]  # Truncate to the maximum number of words
    return ' '.join(words)

def get_sentiment(text, retries=3, wait_time=10):

    cleaned_text = remove_stopwords(text)
    truncated_text = truncate_text(cleaned_text)

    url = API_URL
    headers = {
        'Authorization': f'Bearer hf_{TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "inputs": truncated_text
    }
    
    for attempt in range(retries):
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json()[0]
        else :
            print(f"Model is loading, retrying in {wait_time} seconds... (Attempt {attempt + 1}/{retries})")
            time.sleep(wait_time)  # Wait before retrying
    
    print("Model failed to load after several attempts.")
    return None

def sentiment_analysis(**kwargs):

    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Reddit Sentiment Analysis")
    parser.add_argument('--game', type=str, required=True, help='Name of the game')
    # Parse the arguments
    args = parser.parse_args()
    # Access the GAME argument
    GAME = args.game

    # Initialize Spark
    spark = SparkSession.builder.appName("Reddit-Sentiment-Analysis") \
            .master(SPARK_MASTER_URL) \
            .getOrCreate()
    print("Spark session created.")

    # Specify the filename
    filepath = f'{OUTPUT_PATH}/data.json'

    # Read the JSON file and load it into a Python object
    with open(filepath, 'r') as json_file:
        data = json.load(json_file)
    
    os.remove(filepath)

    # Convert the cleaned data to a DataFrame
    posts_rdd = spark.sparkContext.parallelize(data)
    posts_df = spark.read.json(posts_rdd)

    # Optionally, iterate through posts and get sentiment
    for row in posts_df.collect():
        top_comments = sorted(row.comments, key=lambda x: x['score'], reverse=True)[:N_TOP_COMMENT] ### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        comment_sentiments = []
        
        # Get sentiment for each top comment
        for comment in top_comments :
            sentiment = get_sentiment(comment['body'])
            res = {'comment': comment['body'], 'results': sentiment, 'score': comment['score']}
            comment_sentiments.append(res)
        
        # Print the results
        for idx, _ in enumerate(top_comments):
            print(f"Comment {idx + 1} Sentiment: {res['results']}")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PWD,
        port=POSTGRES_PORT
    )
    cur = conn.cursor()

    # Create a table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            game VARCHAR(50) NOT NULL,
            comment TEXT NOT NULL,
            score INT NOT NULL,
            positive_score NUMERIC(10, 8),
            negative_score NUMERIC(10, 8),
            neutral_score NUMERIC(10, 8)
        );
    """)
    conn.commit()

    # Insert data into PostgreSQL
    insert_query = f"""
        INSERT INTO comments (game, comment, score, positive_score, negative_score, neutral_score)
        VALUES ('{GAME}', %s, %s, %s, %s, %s)
    """

    for sentiment in comment_sentiments:
        comment_text = sentiment['comment']
        score = sentiment['score']
        
        # Extract sentiment scores
        positive_score = next((s['score'] for s in sentiment['results'] if s['label'] == 'positive'), None)
        negative_score = next((s['score'] for s in sentiment['results'] if s['label'] == 'negative'), None)
        neutral_score = next((s['score'] for s in sentiment['results'] if s['label'] == 'neutral'), None)

        # Execute the insert query
        cur.execute(insert_query, (comment_text, score, positive_score, negative_score, neutral_score))

    # Commit changes to the database
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()

    print("JOB IS DONE!")
    
    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    sentiment_analysis()

# API OUTPUT EXAMPLE
# [[{'label': 'negative', 'score': 0.4995437264442444}, {'label': 'positive', 'score': 0.34126028418540955}, {'label': 'neutral', 'score': 0.1591959297657013}]]