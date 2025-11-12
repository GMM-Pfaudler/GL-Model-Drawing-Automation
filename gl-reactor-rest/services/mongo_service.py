from repositories.mongo_db import Mongo
from pymongo.errors import PyMongoError
class mongoService ():
    def __init__(self):
        self.db = Mongo()

    def insert_or_create_collection(self, collection_name, document):
        """
        Insert a document into a collection. If the collection does not exist, it will be created automatically.
        """
        try:
            collection = self.db[collection_name]  # MongoDB will create this collection if it doesn't exist
            result = collection.insert_one(document)
            print(f"Document inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"Error inserting document: {e}")
            return None

    
    def update_by_reactor(self, collection_name, reactor_name, update_data):
        """
        Update a document in the given collection where 'reactor' matches reactor_name.
        """
        try:
            collection = self.db[collection_name]

            # Optional: Ensure update_data reactor matches the document reactor
            if "reactor" in update_data and update_data["reactor"] != reactor_name:
                print("⚠️ Reactor mismatch. Update aborted.")
                return 0

            result = collection.update_one(
                {"reactor": reactor_name},  # Filter document by reactor field
                {"$set": update_data}       # Fields to update
            )
            return result.modified_count

        except PyMongoError as e:
            print(f"Error updating document by reactor: {e}")
            return 0
