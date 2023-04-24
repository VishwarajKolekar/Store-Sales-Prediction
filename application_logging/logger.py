import pymongo
from datetime import datetime
from env_variable import MONGODB_URL_KEY
import os

class App_Logger:
    def __init__(self):

        mongo_db_url = os.getenv(MONGODB_URL_KEY)
        self.client = pymongo.MongoClient(mongo_db_url)
        




    def log(self, db, collection, tag, log_message):
        database = self.client[db]
        collection = database[collection]
        record={
            "timestamp" : str(datetime.now()),
            "tag" : tag,
            "log_message" : log_message
        }

        collection.insert_one(record)
