import re
import json
from utils.constants import OUTPUT_PATH

# Define a cleaning function
def clean_text(text):
    # Lowercase the text
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove special characters and punctuation, but keep basic punctuation like .,!? for sentiment analysis
    text = re.sub(r'[^\w\s.,!?]', '', text)
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Function to clean the JSON data
def clean_json_data(json_data):
    cleaned_data = []
    
    for post in json_data:
        # Remove posts where the body is "[removed]"
        if post.get('body', '').strip() == '[removed]':
            continue
        
        # Clean the post body
        post['body'] = clean_text(post.get('body', ''))
        
        # Check and clean comments
        if 'comments' in post:
            cleaned_comments = []
            for comment in post['comments']:
                # Remove comments where the body is "[removed]"
                if comment.get('body', '').strip() != '[removed]':
                    # Clean the comment body
                    comment['body'] = clean_text(comment.get('body', ''))
                    cleaned_comments.append(comment)
            post['comments'] = cleaned_comments
        
        cleaned_data.append(post)
    
    return cleaned_data


def data_cleaner(**kwargs) :

    # Retrieve the path from the previous task's XCom
    ti = kwargs['ti']
    posts_data = ti.xcom_pull(task_ids='reddit_extract')

    # Clean the data
    cleaned_data = clean_json_data(posts_data)

    print("Data cleaning complete!")

    filepath = f'{OUTPUT_PATH}/data.json'
    # Save the list of dictionaries to a JSON file
    with open(filepath, 'w') as json_file:
        json.dump(cleaned_data, json_file, indent=4, default=str)  # indent for pretty printing

    return cleaned_data
