import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)

# Access the database
db = client['github_webhooks']

# Access the collection
collection = db['events']
