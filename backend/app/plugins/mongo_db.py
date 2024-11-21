import pymongo
from config import settings


class MongoClient:
    def __init__(self):
        self.client = pymongo.MongoClient(settings.MONGO_DB)
        self.db = self.client["orgbook-publisher"]

    def provision(self):
        self.db["credentials"]
        self.db["statusCedentials"]

    def insert(self, collection, item):
        self.db[collection].insert_one(item)

    def find(self, collection, query):
        return self.db[collection].find(query)

    def update(self, collection, query, new_item):
        self.db[collection].update_one(query, new_item)

    def delete(self, collection, query):
        self.db[collection].delete_one(query)
