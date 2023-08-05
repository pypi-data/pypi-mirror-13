from pymongo import MongoClient


class IMongoDB():
    def __init__(self, database, collection, host='localhost', port=27017):
        self._client = MongoClient(host, port)  # could throw
        self._initialize_database(database, collection)

    def insert(self, dataDict):
        return self._collection.insert_many(dataDict)

    def find(self, query):
        return self._collection.find(query)

    def _initialize_database(self, database, collection):
        self._database = self._client[database]
        self._collection = self._database[collection]
