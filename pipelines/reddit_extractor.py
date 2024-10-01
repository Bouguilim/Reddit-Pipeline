import os
import praw
import json
import time
import datetime
from utils.constants import *


def reddit_extractor(game) :

    # Create a unique ID based on local time
    def generate_uid():
        return str(int(time.time() * 1000))  # milliseconds precision

    # Load scraped post IDs from file
    def load_scraped_ids(file_path='scraped_posts.txt'):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return set(line.strip() for line in f)
        return set()

    # Save new scraped post IDs
    def save_scraped_ids(post_ids, file_path=f'{INPUT_PATH}/scraped_posts.txt'):
        with open(file_path, 'a') as f:
            for post_id in post_ids:
                f.write(post_id + '\n')

    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USERAGENT,
        username=USERNAME,
        password=PASSWORD
    )

    # Define query and subreddit search
    query = game
    subreddit_search = reddit.subreddit("patientgamers").search(query=query)

    # Load previously scraped IDs
    scraped_post_ids = load_scraped_ids()

    # Container for new scraped post IDs
    new_post_ids = set()
    posts_data = []

    # Iterate over search results and limit to 10 posts
    post_count = 0

    for submission in subreddit_search:
        if post_count >= POST_LIMIT:
            break
        
        if submission.id in scraped_post_ids:
            continue

        # Post level data
        post_data = {
            "uid": generate_uid(),
            "date": datetime.datetime.fromtimestamp(int(submission.created_utc)),
            "title": submission.title,
            "body": submission.selftext,
            "score": submission.score,
            "num_of_comments": submission.num_comments,
            "comments": []
        }

        # Fetch comments
        submission.comments.replace_more(limit=0)  # Load all comments
        for comment in submission.comments.list():
            comment_data = {
                "date": datetime.datetime.fromtimestamp(int(comment.created_utc)),
                "body": comment.body,
                "score": comment.score
            }
            post_data["comments"].append(comment_data)

        posts_data.append(post_data)
        new_post_ids.add(submission.id)  # Add post ID to new set
        post_count += 1  # Increment post count

        # Delay to avoid hitting rate limit
        time.sleep(2)  # Wait 2 seconds between requests (adjust as needed)

    # Save the new scraped post data to JSON file
    if posts_data:
        file_path = f'{OUTPUT_PATH}/reddit_comments.json'
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=4, default=str)
        print("Successful Extraction !")

    # Save new scraped post IDs to file
    save_scraped_ids(new_post_ids)
    print(f"Scraped {len(new_post_ids)} new posts.")

    # Return the file path for use in the next task
    return file_path