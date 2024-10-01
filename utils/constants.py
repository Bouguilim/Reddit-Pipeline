import configparser
import os

parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), '../config/config.conf'))

# reddit api
CLIENT_ID = parser.get('reddit_api', 'CLIENT_ID')
CLIENT_SECRET = parser.get('reddit_api', 'CLIENT_SECRET')
USERAGENT = parser.get('reddit_api', 'USERAGENT')
USERNAME = parser.get('reddit_api', 'USERNAME')
PASSWORD = parser.get('reddit_api', 'PASSWORD')

# pipeline param
POST_LIMIT = int(parser.get('pipeline', 'POST_LIMIT'))

# paths
INPUT_PATH = parser.get('file_paths', 'INPUT_PATH')
OUTPUT_PATH = parser.get('file_paths', 'OUTPUT_PATH')