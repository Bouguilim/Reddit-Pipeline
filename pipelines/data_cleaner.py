import re
import json

def data_cleaner(**kwargs) :

    # Retrieve the path from the previous task's XCom
    ti = kwargs['ti']
    input_file = ti.xcom_pull(task_ids='reddit_extract')

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

    file_path = input_file

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Clean the data
    cleaned_data = clean_json_data(data)

    # Save the cleaned JSON back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    print("Data cleaning complete!")

    return file_path
