import configparser
import os

parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), '../config/config.conf'))

# postgres
POSTGRES_HOST = parser.get('postgres', 'POSTGRES_HOST')
POSTGRES_DB = parser.get('postgres', 'POSTGRES_DB')
POSTGRES_USER = parser.get('postgres', 'POSTGRES_USER')
POSTGRES_PWD = parser.get('postgres', 'POSTGRES_PWD')
POSTGRES_PORT = int(parser.get('postgres', 'POSTGRES_PORT'))

# mongodb
MONGO_URL = parser.get('mongodb', 'MONGO_URL')

# spark
SPARK_MASTER_URL = parser.get('spark', 'SPARK_MASTER_URL')

# reddit api
CLIENT_ID = parser.get('reddit_api', 'CLIENT_ID')
CLIENT_SECRET = parser.get('reddit_api', 'CLIENT_SECRET')
USERAGENT = parser.get('reddit_api', 'USERAGENT')
USERNAME = parser.get('reddit_api', 'USERNAME')
PASSWORD = parser.get('reddit_api', 'PASSWORD')

# huggingface api
TOKEN = parser.get('huggingface_api', 'TOKEN')
API_URL = parser.get('huggingface_api', 'API_URL')

# pipeline param
GAME = parser.get('pipeline', 'GAME')
SCHEDULE_INTREVAL = parser.get('pipeline', 'SCHEDULE_INTREVAL')
POST_LIMIT = int(parser.get('pipeline', 'POST_LIMIT'))
N_TOP_COMMENT = int(parser.get('pipeline', 'N_TOP_COMMENT'))

# paths
INPUT_PATH = parser.get('file_paths', 'INPUT_PATH')
OUTPUT_PATH = parser.get('file_paths', 'OUTPUT_PATH')