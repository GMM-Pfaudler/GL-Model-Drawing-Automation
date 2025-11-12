import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from dotenv import load_dotenv
load_dotenv()
mongo_uri = os.getenv('MONGO_URI')

class Mongo:
    def __init__(self, db=None):
        """
        Initialize the MongoDB connection and select the database.
        """
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db]
            print(f"Connected to MongoDB database: {db}")
        except PyMongoError as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None

    # ----------------------------
    # CREATE
    # ----------------------------
    def insert(self, collection_name, document):
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error inserting document: {e}")
            return None

    # ----------------------------
    # READ
    # ----------------------------
    def find(self, collection_name, query=None):
        try:
            collection = self.db[collection_name]
            if query is None:
                query = {}
            documents = collection.find(query)
            return list(documents)
        except PyMongoError as e:
            print(f"Error finding documents: {e}")
            return []

    def find_one_by_name(self, collection_name, name):
        try:
            collection = self.db[collection_name]
            document = collection.find_one({"name": name})
            return document
        except PyMongoError as e:
            print(f"Error finding document by name: {e}")
            return None

    # ----------------------------
    # UPDATE
    # ----------------------------
    def update(self, collection_name, document_id, update_data):
        try:
            collection = self.db[collection_name]
            result = collection.update_one(
                {"_id": ObjectId(document_id)}, {"$set": update_data}
            )
            return result.modified_count
        except PyMongoError as e:
            print(f"Error updating document: {e}")
            return 0

    # ----------------------------
    # DELETE
    # ----------------------------
    def delete(self, collection_name, document_id):
        try:
            collection = self.db[collection_name]
            result = collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count
        except PyMongoError as e:
            print(f"Error deleting document: {e}")
            return 0


# ----------------------------
# Example Usage
# ----------------------------
# if __name__ == "__main__":
#     # Initialize MongoDB connection
#     mongo = Mongo(db="testdb")

#     # Insert a document
#     doc_id = mongo.insert("students", {"name": "Alice", "age": 30})
#     print("Inserted ID:", doc_id)

    # # Find documents
    # docs = mongo.find("students", {"age": {"$gte": 25}})
    # print("Found Documents:", docs)

    # # Find one by name
    # doc = mongo.find_one_by_name("students", "Alice")
    # print("Found Document by Name:", doc)

    # # Update document
    # updated_count = mongo.update("students", doc_id, {"age": 31})
    # print("Updated Documents Count:", updated_count)

    # Delete document
    # deleted_count = mongo.delete("my_collection", doc_id)
    # print("Deleted Documents Count:", deleted_count)
